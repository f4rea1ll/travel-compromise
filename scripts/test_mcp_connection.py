import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

load_dotenv()

MCP_URL = os.getenv("MCP_SERVER_URL")


async def main():
    print(f"Подключаюсь к {MCP_URL} ...")
    async with streamable_http_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Соединение установлено, запрашиваю список инструментов...\n")

            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"— {tool.name}")
                print(f"  {tool.description}\n")

            print("\n--- Тестовый поиск: Москва → Казань ---\n")
            result = await session.call_tool(
                "search_multitransport",
                arguments={
                    "origin": "Москва",
                    "destination": "Казань",
                    "departure_date": "2026-09-01",
                },
            )
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text[:3000])
                    
if __name__ == "__main__":
    asyncio.run(main())