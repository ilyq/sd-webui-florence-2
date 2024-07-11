import launch

# TypeError: Object of type Florence2LanguageConfig is not JSON serializable
try:
    print("Installing requirements for florence")
    launch.run_pip("install -U transformers>=4.41.2", "requirements for transformers")
except Exception as e:
    print(f"Warning: upgrade transformers failed: {e}")
