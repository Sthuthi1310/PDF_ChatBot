
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering


class RoBERTaQuestionAnswering:

    def __init__(self):

        print("Loading RoBERTa Question Answering model...")

        model_name = "deepset/roberta-base-squad2"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForQuestionAnswering.from_pretrained(
            model_name
        )

        self.model.eval()

        print("RoBERTa model loaded successfully!")

    def answer(self, question, context):

        if not question or not context:
            return {
                "answer": "No relevant answer found.",
                "score": 0.0
            }

        inputs = self.tokenizer(
            question,
            context,
            return_tensors="pt",
            truncation="only_second",
            max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        start_logits = outputs.start_logits[0]
        end_logits = outputs.end_logits[0]

        # Find the most likely starting token
        start_index = torch.argmax(start_logits).item()

        # Find the best ending token within 30 tokens
        max_end_index = min(
            start_index + 30,
            len(end_logits) - 1
        )

        end_index = (
            torch.argmax(
                end_logits[start_index:max_end_index + 1]
            ).item() + start_index
        )

        # Extract answer tokens
        answer_tokens = inputs["input_ids"][0][
            start_index:end_index + 1
        ]

        answer = self.tokenizer.decode(
            answer_tokens,
            skip_special_tokens=True
        ).strip()

        # Calculate a relative confidence score
        score = torch.softmax(
            start_logits, dim=0
        )[start_index] * torch.softmax(
            end_logits, dim=0
        )[end_index]

        return {
            "answer": answer if answer else "No relevant answer found.",
            "score": round(score.item(), 4)
        }
