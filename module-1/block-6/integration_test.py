import subprocess
import time

STUDENT_NAME = "selector0073"
IMAGE_TAG_2_0 = f"{STUDENT_NAME}-app:2.0"
IMAGE_TAG_1_0 = f"{STUDENT_NAME}-app:1.0"
CONTAINER_NAME = f"{STUDENT_NAME}-app-container"


def run_cmd(command: str, check_output: bool = True) -> str:
    print(f"\n[EXEC] > {command}")
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        check=False
    )
    
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr and result.returncode != 0:
        print(f"[ERROR] {result.stderr.strip()}")
        
    if check_output and result.returncode != 0:
        raise RuntimeError(f"Command execution failed (exit code {result.returncode})")
        
    return result.stdout.strip()


def main():
    print(f"=== Starting integration test for: {STUDENT_NAME} ===")

    try:
        print("\n---> Step 1: Building image version 2.0")
        run_cmd(
            f'docker build '
            f'--build-arg STUDENT_NAME="{STUDENT_NAME}" '
            f'-t {IMAGE_TAG_2_0} .'
        )

        print("\n---> Step 2: Running container in detached mode")
        run_cmd(
            f'docker run -d '
            f'--name {CONTAINER_NAME} '
            f'-e STUDENT_NAME="{STUDENT_NAME}" '
            f'{IMAGE_TAG_2_0}'
        )

        time.sleep(2)

        print("\n---> Step 3: Verifying container logs")
        logs = run_cmd(f'docker logs {CONTAINER_NAME}')
        if STUDENT_NAME in logs:
            print(f" SUCCESS: Name '{STUDENT_NAME}' detected in logs.")
        else:
            print(f" WARNING: Name '{STUDENT_NAME}' was not found in logs.")

        print("\n---> Step 4: Verifying STUDENT_NAME environment variable via docker exec")
        env_val = run_cmd(f'docker exec {CONTAINER_NAME} printenv STUDENT_NAME')
        print(f"Evaluated STUDENT_NAME in container: '{env_val}'")
        assert env_val == STUDENT_NAME, f"Expected '{STUDENT_NAME}', received '{env_val}'"

    finally:
        print("\n---> Step 5: Stopping and removing container")
        run_cmd(f'docker stop {CONTAINER_NAME}', check_output=False)
        run_cmd(f'docker rm {CONTAINER_NAME}', check_output=False)

        print("\n---> Step 6: Purging Docker images")
        run_cmd(f'docker rmi -f {IMAGE_TAG_1_0} {IMAGE_TAG_2_0}', check_output=False)

    print("\n=== Integration test completed successfully ===")


if __name__ == "__main__":
    main()