import os
import subprocess
import redis
from core.config import settings

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(error.decode())
        exit(1)
    return output.decode()

def reset_database():
    # Step 1: Drop all tables
    print("Dropping all tables...")
    run_command("alembic downgrade base")

    # Step 2: Remove all migration files
    print("Removing all migration files...")
    migrations_dir = "alembic/versions"
    for file in os.listdir(migrations_dir):
        if file.endswith(".py"):
            os.remove(os.path.join(migrations_dir, file))

    # Step 3: Recreate initial migration
    print("Creating new initial migration...")
    run_command("alembic revision --autogenerate -m 'Initial migration'")

    # Step 4: Apply the new migration
    print("Applying new migration...")
    run_command("alembic upgrade head")

    print("Database reset complete!")
    
def reset_redis_cache():
    redis_client = redis.Redis.from_url(settings.REDIS_URL)
    redis_client.flushdb()
    print("Redis cache has been reset successfully!")

def reset_all():
    reset_database()
    reset_redis_cache()
    print("Both database and Redis cache have been reset!")

if __name__ == "__main__":
    reset_all()
    reset_database()