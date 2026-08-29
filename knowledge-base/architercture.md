#整体框架
architecture-beta
    group frontend(cloud)[Vue3]
    group backend(cloud)[FastAPI]
    group repository(cloud)[Postgresql]
    group disk(disk)[Disk]
    
    service user(internet)[users] in frontend
    service web(internet)[Website] in frontend
    service api(server)[API Router] in backend
    service auth(server)[Module Services] in backend
    service files(disk)[File Storage] in disk

    service db(database)[Database] in repository

    user:B --> T:web

    web:R --> L:api
    api:R --> L:auth
    auth:R -- L:files

    auth:B -- T:db

#部署框架
architecture-beta
    group localserver(server)[localserver]
        group env_setting(server)[env_setting] in localserver
            service env_file(server)[env_file] in env_setting
            service appsettings(server)[AppSettings]in env_setting

            env_file:R -- L:appsettings
        service docker(server)[docker] in localserver