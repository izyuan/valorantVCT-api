from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from importlib import import_module


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def import_routers(directory, package_prefix):
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith('.py') and entry.name != '__init__.py':
            module_name = entry.name[:-3]
            module_path = f'{package_prefix}.{module_name}'
            print(f"loading {module_path}")
            endpoint_module = import_module(module_path)
            try:
                if module_name == 'docs':
                    app.include_router(endpoint_module.router)
                    print(f"loading {endpoint_module}")
                    continue
                else:
                    app.include_router(endpoint_module.router,
                                       prefix=f"/{package_prefix.split('.')[-1]}",
                                       ),

            except AttributeError as e:
                print("Failed to import " + module_path, e)
                pass
        elif entry.is_dir():
            new_package_prefix = f'{package_prefix}.{entry.name}'
            import_routers(entry.path, new_package_prefix)


endpoints_dir = os.path.join(os.path.dirname(__file__), "routers")
import_routers(endpoints_dir, 'routers')


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=6001, reload=True)
