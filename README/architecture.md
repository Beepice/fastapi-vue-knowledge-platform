flowchart architecture
    subgraph python_env["be ready for environment"]
        style python_env fill: #0000
        venv["python3.12 create .venv"] --> |.venv's python| poetry["virtual pip"]
        poetry -->|pip install poetry| poetry_install["virtual poetry"]
        poetry_install-->|poetry install|ready_python[("virtual python environment")]

        npm_env_install["installed nodejs 20+"] --> knowledge_dir["entry into knowledge-base"]
        knowledge_dir --> |npm install|npm_install
        npm_install["ready npm library"] --> |npm run build|npm_dist[("dist for vue3 environemt")]
    
        docker_sql["make sure docker env for windows"] --> |docker-composed -d db| docker_postgresql[(ready postgresql with 15.4 env for windows)]
        docker_postgresql-->default_sql_server["start sql service and default port on 5432"]

        linux_sql["make sure postgresql with version 15"]-->|apt install postgres-15-pgvectory|ready_sql[("ready postgresql with 15 env for linux")]
        ready_sql-->default_sql_server
    end

    subgraph db_manager["database manage"]
        style db_manager fill: #0000
        ready_python-->alembic_ini
        alembic_ini["alembic.init"]-->|script_location|alembic_env["alembic's env file"]
        alembic_env --> |alembic version manage|Postgresql[(Postgresql 15)]
        default_sql_server <-->|alive service|Postgresql
    end

    subgraph env_getting["env_getting"]
        style env_getting fill: #0000
        env_file[.env file] --> |Base setting| appsetting["AppSetting class"]
        appsetting --> |get_app_setting| alembic_env
        

    end

    subgraph local["run app"]
        style local fill: #0000

        subgraph fastapi["fastapi"]
            style fastapi fill: #0000
            subgraph lifespan["lifespan"]
                appsetting --> |get_app_setting| data_url["data_url"]
                data_url-->asyncpg["asyncpg.create_pool"]
                asyncpg --> |database operation|Postgresql
                asyncpg -->|connect_to_db|app_start -.->|continous requires|asyncpg
                app_start-->app_done
                app_done-->|close_connection_to_db|asyncpg
            end

            appsetting-->|get_app_setting|setting
            setting-->|self.configure_logging|handled_logger["logger setting"]
            handled_logger-->|FastAPI|create_APP["registerize FastAPI app"]
            lifespan -->create_APP
            create_APP-->|FastAPI.add_middleware|middle_setting["middleware setting"]
            middle_setting-->|FastAPI.add_exception_handler|handled_error
            handled_error-->|FastAPI.include_router|app["FastAPI app with register services"]
            npm_dist-->|SPA integrated method|app_mount["app with mounted dist"]-->app
            app-->uvircon["uvicorn start the app"]
        
        end
    end

