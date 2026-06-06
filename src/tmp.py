import asyncio

from external_api.router_ai import RouterAiApi


async def main():
    api = RouterAiApi()
    models = await api.get_models()
    print(models[0])

    print(f"Количество моделей: {len(models)}")
    models_ids = [model["id"] for model in models]
    print(f"id моделей: {models_ids}")


if __name__ == "__main__":
    asyncio.run(main())
