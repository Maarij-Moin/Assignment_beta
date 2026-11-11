# Assignment Beta — Agentic AI (AI4015)

**Institution:** National University of Computer and Emerging Sciences (FAST NUCES), Karachi  
**Student ID:** 22K-8706  
**Semester:** Fall 2026  
**Course Instructor:** Dr. Muhammad Farrukh Shahid  

---

## Repository Structure

```text
├── Question_1/
│   ├── Assignment_Beta_Question_no_1_22K-8706.docx    # Written feasibility report & sizing
│   ├── Assignment_Beta_Question_no_1_22K-8706.ipynb   # Executed token & cost calculation notebook
│   ├── cost_breakeven_plot.png                        # Step-function break-even visualization
│   ├── build_q1.py                                    # Master generator script
│   └── tool_latency/
│       ├── measure_tool_latency.py                    # Live API & local measurement script
│       └── raw_tool_latency_log.csv                   # 100 empirical timing logs across 2 dates
├── Question_2/
│   └── Assignment_Beta_Question_no_2_22K-8706.ipynb   # PEFT comparison (LoRA, QLoRA, DoRA, AdaLoRA)
├── Question_3/
│   ├── Assignment_Beta_Question_no_3_22K-8706.docx    # Step-by-step Knowledge Distillation solution
│   └── Assignment_Beta_Question_no_3_22K-8706.ipynb   # Executed notebook with exact math & gradients
├── Question_4/
│   ├── Assignment_Beta_Question_no_4_22K-8706.docx    # LLM Sentiment Evaluator report & CIs
│   ├── Assignment_Beta_Question_no_4_22K-8706.ipynb   # Executed evaluation notebook (BLEU, ROUGE, PPL)
│   └── confusion_matrices.png                         # High-res Stage 1 vs Stage 2 confusion matrices
└── Question_5/
    └── Assignment_Beta_Question_no_5_22K-8706.docx    # 2-page summary of Ersoy & Erşahin (2025)
```

---

## Overview of Questions

1. **Question 1: Closed-Source API vs. Self-Hosting for SaafHawa Agent**
   - Parameters: $R=6, D=5 \implies Q=1,650, N=7, p=0.09, H=6, B=\$1,260, T=10.0\text{ s}$.
   - Evaluates 12 models (6 closed, 6 open) across 4 providers each.
   - Sizing and break-even analysis for self-hosting Llama-3.1-8B on an RTX 4090 ($316.80/mo).
   - Architectural redesign (parallel tool calling + streaming) to meet $T \le 10\text{ s}$.

2. **Question 2: Parameter-Efficient Fine-Tuning for Function Calling**
   - Base model: `Qwen/Qwen2.5-1.5B-Instruct` on `glaive-function-calling-v2`.
   - Compares LoRA, QLoRA, DoRA, and AdaLoRA against the un-tuned base model.
   - Rank sweep ($r \in \{4, 8, 16, 32\}$), error taxonomy, and adapter merging speedup.

3. **Question 3: Knowledge Distillation Worked Calculation**
   - Vocabulary: `{hospital, clinic, ward, school}` with gold label `hospital`.
   - Softened probabilities at $T=2$, $\text{KL}(p^T \parallel q^T) = 0.081607\text{ nats}$, $\text{CE} = 0.601005$, Loss $L = 0.463717$.
   - Analytical gradient w.r.t student logits and 1 gradient descent step ($\eta=0.5 \implies L'=0.349256$).

4. **Question 4: LLM Sentiment Classifier Evaluation**
   - 300 reviews across 3 classes (Positive, Negative, Neutral).
   - Stage 1 zero-shot ($76.67\% \pm 4.8\%$) vs. Stage 2 few-shot ($84.67\%$).
   - Justification evaluation: $\text{BLEU-4} = 0.4750, \text{ROUGE-1} = 0.8421, \text{METEOR} = 0.7868, \text{PPL} = 2.3249$.

5. **Question 5: RAG Architectures Survey Paper Summary**
   - 2-page synthesis of P. Ersoy and M. Erşahin, *"A Comparative Evaluation of RAG Architectures for Cross-Domain LLM Applications: Design, Implementation, and Assessment"*, *IEEE Access*, vol. 13, 2025.
