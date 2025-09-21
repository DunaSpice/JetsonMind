#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
    char input[1024];
    int choice;
    
    printf("Phase 3 C Frontend v1.0 (Test Mode)\n");
    printf("Note: This is a test version with mock responses\n");
    
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
                printf("Generated: Mock text for '%s'\n", input);
                break;
                
            case 2:
                printf("Status: {\n");
                printf("  \"status\": \"healthy\",\n");
                printf("  \"server\": \"phase3-admin\",\n");
                printf("  \"version\": \"1.0.0\",\n");
                printf("  \"frontend_running\": true\n");
                printf("}\n");
                break;
                
            case 3:
                printf("Frontend: Started on port 8080\n");
                break;
                
            case 4:
                printf("Debug level (0-3): ");
                scanf("%d", &choice);
                printf("Debug: Level set to %d\n", choice);
                break;
                
            case 5:
                printf("Config: {\n");
                printf("  \"model\": \"gpt-4\",\n");
                printf("  \"temperature\": 0.7,\n");
                printf("  \"max_tokens\": 1000\n");
                printf("}\n");
                break;
                
            case 6:
                printf("Database: {\n");
                printf("  \"connected\": true,\n");
                printf("  \"sessions\": 0,\n");
                printf("  \"settings\": 3\n");
                printf("}\n");
                break;
                
            case 7:
                printf("Settings: {\n");
                printf("  \"debug_level\": 1,\n");
                printf("  \"frontend_port\": 8080,\n");
                printf("  \"agent_model\": \"gpt-4\"\n");
                printf("}\n");
                break;
                
            case 8:
                printf("Goodbye!\n");
                return 0;
                
            default:
                printf("Invalid choice\n");
        }
    }
}
