#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <curl/curl.h>
#include <json-c/json.h>

#define MAX_RESPONSE 4096
#define MAX_INPUT 1024

typedef struct {
    char *data;
    size_t size;
} Response;

static size_t WriteCallback(void *contents, size_t size, size_t nmemb, Response *response) {
    size_t realsize = size * nmemb;
    char *ptr = realloc(response->data, response->size + realsize + 1);
    if (!ptr) return 0;
    
    response->data = ptr;
    memcpy(&(response->data[response->size]), contents, realsize);
    response->size += realsize;
    response->data[response->size] = 0;
    return realsize;
}

int call_mcp_tool(const char *tool, const char *args, char *result) {
    CURL *curl;
    CURLcode res;
    Response response = {0};
    
    curl = curl_easy_init();
    if (!curl) return -1;
    
    // Create JSON-RPC request
    json_object *request = json_object_new_object();
    json_object *jsonrpc = json_object_new_string("2.0");
    json_object *method = json_object_new_string("tools/call");
    json_object *id = json_object_new_int(1);
    json_object *params = json_object_new_object();
    json_object *name = json_object_new_string(tool);
    json_object *arguments = json_tokener_parse(args);
    
    json_object_object_add(params, "name", name);
    json_object_object_add(params, "arguments", arguments);
    json_object_object_add(request, "jsonrpc", jsonrpc);
    json_object_object_add(request, "method", method);
    json_object_object_add(request, "id", id);
    json_object_object_add(request, "params", params);
    
    const char *json_string = json_object_to_json_string(request);
    
    // Setup curl for local MCP server
    curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:8080/mcp");
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_string);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    
    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    
    res = curl_easy_perform(curl);
    
    if (res == CURLE_OK && response.data) {
        strncpy(result, response.data, MAX_RESPONSE - 1);
        result[MAX_RESPONSE - 1] = '\0';
    }
    
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    json_object_put(request);
    if (response.data) free(response.data);
    
    return (res == CURLE_OK) ? 0 : -1;
}

void print_menu() {
    printf("\n=== Phase 3 Control Panel ===\n");
    printf("1. Generate Text\n");
    printf("2. System Status\n");
    printf("3. Start Frontend\n");
    printf("4. Debug Mode\n");
    printf("5. Agent Config\n");
    printf("6. Database Management\n");
    printf("7. Settings\n");
    printf("8. Exit\n");
    printf("Choice: ");
}

int main() {
    char input[MAX_INPUT];
    char result[MAX_RESPONSE];
    int choice;
    
    curl_global_init(CURL_GLOBAL_DEFAULT);
    
    printf("Phase 3 C Frontend v1.0\n");
    
    while (1) {
        print_menu();
        if (scanf("%d", &choice) != 1) {
            printf("Invalid input\n");
            continue;
        }
        
        switch (choice) {
            case 1:
                printf("Enter prompt: ");
                getchar(); // consume newline
                fgets(input, sizeof(input), stdin);
                input[strcspn(input, "\n")] = 0; // remove newline
                
                snprintf(result, sizeof(result), "{\"prompt\":\"%s\"}", input);
                if (call_mcp_tool("generate", result, result) == 0) {
                    printf("Result: %s\n", result);
                } else {
                    printf("Error calling generate tool\n");
                }
                break;
                
            case 2:
                if (call_mcp_tool("get_status", "{}", result) == 0) {
                    printf("Status: %s\n", result);
                } else {
                    printf("Error getting status\n");
                }
                break;
                
            case 3:
                if (call_mcp_tool("start_frontend", "{}", result) == 0) {
                    printf("Frontend: %s\n", result);
                } else {
                    printf("Error starting frontend\n");
                }
                break;
                
            case 4:
                printf("Debug level (0-3): ");
                scanf("%d", &choice);
                snprintf(result, sizeof(result), "{\"level\":%d}", choice);
                if (call_mcp_tool("set_debug", result, result) == 0) {
                    printf("Debug: %s\n", result);
                }
                break;
                
            case 5:
                if (call_mcp_tool("get_agent_config", "{}", result) == 0) {
                    printf("Config: %s\n", result);
                }
                break;
                
            case 6:
                if (call_mcp_tool("db_status", "{}", result) == 0) {
                    printf("Database: %s\n", result);
                }
                break;
                
            case 7:
                if (call_mcp_tool("get_settings", "{}", result) == 0) {
                    printf("Settings: %s\n", result);
                }
                break;
                
            case 8:
                printf("Goodbye!\n");
                curl_global_cleanup();
                return 0;
                
            default:
                printf("Invalid choice\n");
        }
    }
}
