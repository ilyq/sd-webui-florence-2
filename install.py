import launch
import platform


if not launch.is_installed("wheel"):
    print("Installing requirements for florence")
    launch.run_pip("install wheel", "requirements for wheel")


# TypeError: Object of type Florence2LanguageConfig is not JSON serializable
try:
    respnse: str = launch.run("pip list | grep transformers")
    version = respnse.strip().split(" ")[-1]
    if version < "4.41.2":
        print("Installing requirements for florence")
        launch.run_pip("install transformers>=4.41.2", "requirements for transformers")
except Exception as e:
    print(f"Warning: upgrade transformers failed: {e}")


if platform.system() == "Linux":
    if not launch.is_installed("packaging"):
        print("Installing requirements for florence")
        launch.run_pip("install packaging", "requirements for packaging")

    # https://pypi.org/project/flash-attn/
    if not launch.is_installed("flash-attn"):
        print("Installing requirements for florence")
        launch.run_pip(
            "install flash-attn --no-build-isolation", "requirements for flash-attn"
        )
