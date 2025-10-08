from guardrails import Guard

gard=Guard()
result = gard(
    messages=[{"role":"user", "content":"How many moons does Jupiter have?"}],
    model="gpt-4o",
    
)

print(f"{result.validated_output}")