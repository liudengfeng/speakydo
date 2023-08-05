# speakydo

Immersive speaking practice using LLAMA models

## Llama Model

1. 参考[llama cpp](https://github.com/ggerganov/llama.cpp) Quantized size (4-bit)


| Model | Original size | Quantized size (4-bit) |
| ----: | ------------: | ---------------------: |
|    7B |         13 GB |                 3.9 GB |
|   13B |         24 GB |                 7.8 GB |
|   30B |         60 GB |                19.5 GB |
|   65B |        120 GB |                38.5 GB |

2. 模型存放目录 `~/llm-models/cpp/`
   1. `llama-2-7B-chat-ggml-q4_0.bin`
   2. `llama-2-13B-chat-ggml-q4_0.bin`

## WSL2
+ [Install the Speech SDK](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/quickstarts/setup-platform?tabs=linux%2Cubuntu)