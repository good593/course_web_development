from dataclasses import dataclass


@dataclass
class UsageStats:
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def record(self, input_tokens: int, output_tokens: int) -> None:
        self.total_requests += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

    def estimated_cost(self) -> float:
        return (
            self.total_input_tokens / 1_000_000 * 0.075
            + self.total_output_tokens / 1_000_000 * 0.30
        )


stats = UsageStats()
