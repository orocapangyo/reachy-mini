# HF_Project

- DistilBERT 기반 감정 분석 프로젝트
  - Hugging Face의 사전 학습된 DistilBERT 모델인
distilbert-base-uncased-finetuned-sst-2-english를 사용하여
텍스트 데이터를 긍정(positive) 또는 부정(negative) 감정으로 분류합니다.

- 데이터셋 정보
  - 입력 데이터는 Dropbox.csv 파일에 저장되어 있어야 합니다.
이 파일에는 content 라는 텍스트 열(column)이 포함되어야 합니다.
전체 데이터 중 무작위로 200개 샘플을 추출하여 분석합니다.

- 주요 기능
  - Dropbox.csv에서 데이터를 불러오고 200개 샘플을 추출합니다.
Hugging Face의 감정 분석 모델로 텍스트 감정을 분류합니다.
배치(batch) 단위로 텍스트를 처리하여 성능과 메모리 사용을 최적화합니다.
감정 분석 결과를 sentiment 열로 추가합니다.
분석된 결과를 출력합니다.

설치 명령어
```
pip install torch transformers pandas
```

📈 사용된 모델 정보
모델 이름: distilbert-base-uncased-finetuned-sst-2-english
출처: [Hugging Face](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)
