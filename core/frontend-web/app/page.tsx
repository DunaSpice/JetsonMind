import { redirect } from "next/navigation";
import { generateUUID } from "@/lib/utils";

export default function HomePage() {
  const chatId = generateUUID();
  redirect(`/chat/${chatId}`);
}
