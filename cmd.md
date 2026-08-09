### Command to start the project dockers 
`docker compose -f docker-compose.dev.yml up -d --build`

### Option 1: Stop and Remove (Recommended)
`docker compose -f docker-compose.dev.yml down`

### Option 2: Just Pause/Stop (Keep containers intact)
`docker compose -f docker-compose.dev.yml stop`

### Option 3: Wipe clean (Including database volumes)
`docker compose -f docker-compose.dev.yml down -v`

### Option 4: Clean up completely (Volumes + Networks + Images)
