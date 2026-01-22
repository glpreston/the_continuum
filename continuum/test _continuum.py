from continuum.orchestrator.continuum_controller import ContinuumController

controller = ContinuumController()

print("\n--- Initialization complete ---\n")

response = controller.process_message("Hello, I feel a bit overwhelmed today.")
print("\n--- Pipeline Output ---\n")
print(response)