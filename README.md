# speakydo

Immersive speaking practice using LLAMA models

## Quantize Llama Model

### `WSL2`中使用`Visual Code`转换`llama-2-13b-chat`模型

#### 克隆[llama cpp](https://github.com/ggerganov/llama.cpp)

#### 在`Visual Code`中编译，使用GPU时在CMAKE UI缓存中修改变量`LLAMA_CUBLAS=ON`

#### 量化`llama-2-13b-chat`模型

- obtain the original LLaMA model weights and place them in ./models
- 从 hugging Face 复制 tokenizer.model
- 激活python环境`conda activate speakydo`
- cd llama.cpp

```bash
# install Python dependencies
python3 -m pip install -r requirements.txt
# convert the 7B model to ggml format
python3 convert.py models/llama-2-13b-chat

cd build/bin
# quantize the model to 4-bits (using q4_0 method)

# 注意将以下路径更为为完全路径
./quantize /home/ldf/github/llama.cpp/models/llama-2-13b-chat/ggml-model-f16.gguf /home/ldf/llm-models/cpp/llama-2-13b-chat-ggml-q4_0.gguf q4_0
# run the inference
./main -m /home/ldf/llm-models/cpp/llama-2-13b-chat-ggml-q4_0.gguf -n 128
```


#### Quantized size (4-bit)


| Model | Original size | Quantized size (4-bit) |
| ----: | ------------: | ---------------------: |
|    7B |         13 GB |                 3.9 GB |
|   13B |         24 GB |                 7.8 GB |
|   30B |         60 GB |                19.5 GB |
|   65B |        120 GB |                38.5 GB |

#### 模型存放目录
   1. `~/llm-models/cpp/`
   2. `llama-2-7B-chat-ggml-q4_0.bin`
   3. `llama-2-13B-chat-ggml-q4_0.bin`

## WSL2
+ [Install the Speech SDK](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/quickstarts/setup-platform?tabs=linux%2Cubuntu)