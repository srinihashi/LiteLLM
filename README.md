# LiteLLM Custom Guardrails

## Introduction

Before we begin, let's take a moment to built some context - ["Introduction"](https://docs.google.com/presentation/d/113l37j2Iu_cNM3habuHdruPWsan5Ng_iw6t_zEbaOUQ/edit?usp=sharing)

## Problem

As we have see from the "Introduction", there are serious concerns especially when using in Enterprises. Here are a few:

- Data & Knowledge
  - Data quality & freshness
  - Data privacy (PII, Sensitive data, etc.)
- Security & Access:
  - RBAC access
  - Data breaches
  - Model poisoning
  - Model misuse
- Governance:
  - Audit loggins and traceability
  - Compliance with standards (PCI, GDPR, HIPPA, etc.)
  - Compliance with regulations (Audits, Compliance, etc.)
- Cost:
  - Spend Tracking (Token usage, Cost, etc.)
  - Budget (Limits, Quotas, etc.)

## Solution

To address these concerns, we need a centralized system that can monitor and control the use of LLMs. Some of the key capabilities of this system:

- A centralized platform to access & use multiple LLMs
- Support guardrails to Control data quality and privacy
- Highly resilient and performant
- Easy to deploy and manage

One such system/platform is [LiteLLM](https://www.litellm.ai/) - It brings all these capabilities into one simple to manage LLM Gateway.
![LiteLLM Architecture](https://i.imgur.com/533222.png)

## Architecture

![LiteLLM Architecture](https://i.imgur.com/533222.png)

Sequence Diagram
![LiteLLM Sequence Diagram](https://sequencediagram.org/index.html?presentationMode=readOnly&shrinkToFit=true#initialData=C4S2BsFMAIGEFcDOwD2BbaBxeBDATgCZ44jgBQZAqopHgLR0B8AFAIwCUAMmJJ5wLIAuJLWgAHPOjHAy3YLwENGchULhJUabPiIlwzEXnGS009rJ59+StuwAKASQcB9WAAtIAYwDWzgMq0AG4gnpCC0IbGUjIqVgA8DI4u7l6+AXjBoYJ4kMDweAB20ADeOJ6gKAXhAIJ8APIA6tAAPtAAQpx1sADSADTQOTiIleHFANoASgCi1X51AHIAugC+y1Q0eAl0sQKCIABmJWUVVe2dPWsFKPLQKIGi1LSCxUnQdijgIQCe0ABqIB8cCc1jtrExbFZwgcjuUAVVap0GiDLAItpCBpBEGJKjQLPIrEpQeEEMh0NpCMRSMwclicZBzKCbBwkq4PD5-EEQmEMbSCrjQVsWSl2elMtzSrCRtBao0Wmcun0MUMpeNprMFit1rQ0Si1NCJSdwh0FZdrjA7g8NqNXu9Pp4fv9AcCtZsGEToPrjnCavUkWQrjcLUZHnhRjTsXzIGsgA)
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Installation

### Pre-Requisites

Please ensure the following pre-requisites have been installed:

- Access to an LLM - Local, Cloud, or AWS Bedrock
- LLM Access Keys (If connecting to a remote LLM)
- Docker (To run LiteLLM Proxy)
- Python (To create custom guardrails)
  - pip
- Postman (To test the API)
- Kubernetes
  - Kubectl
  - Helm


### Installation Steps

#### Deploy LiteLLM Proxy

**Step-1:** Install LiteLLM locally in Docker
Change directory into "litellm-proxy" and complete the following steps.
1-a: Pull the LiteLLM database image
```   $ docker pull ghcr.io/berriai/litellm-database:main-latest```

1-b: Download the docker compose file
```    $ curl -O https://raw.githubusercontent.com/BerriAI/litellm/main/docker-compose.yml```

1-c: Add the master key - you can change this after setup
```   $ echo 'LITELLM_MASTER_KEY="<YOUR_MASTER_KEY>"' > .env```
*NOTE: default is "sk-1234"*

1-d: Add the litellm salt key. Used to encrypt/decrypt your LLM API key credentials
```   $ echo 'LITELLM_SALT_KEY="<YOUR_SALT_KEY>"' >> .env```
*NOTE: default is "sk-1234"*

1-e: Create the “config.yaml” file as follows:

```
      general_settings:
  	    master_key: os.environ/LITELLM_MASTER_KEY
  	    database_url: "postgresql://llmproxy:dbpassword9090@db:5432/litellm"
```

1-f: Create the prometheus.yml file as follows:

```
      global:
        scrape_interval: 15s
        evaluation_interval: 15s

      scrape_configs:
        - job_name: "litellm"
          static_configs:
            - targets: ["litellm:4000"]
```

1-g: Edit the docker-compose.yaml file and verify that the config.yaml volume mount and --config flag are not commented out:

```
      services:
        litellm:
          volumes:
            - ./config.yaml:/app/config.yaml # ✅ must be uncommented
          command:
            - "--config=/app/config.yaml" # ✅ must be uncommented
```

**Step-2:** Start the proxy server and test it
``` $ docker compose up ```

**Step-3:** Navigate to the LiteLLM UI and generate a virtual key
Open http://localhost:4000/ui in your browser and log in with your master key (*default: sk-1234*).

### Configure LLMs

- Configure a local LLM such as llama3.2. Edit config.yml file and add following lines

```
    model_list:
        - model_name: "llama3.2"
          litellm_params:
            model: "ollama_chat/llama3.2"
            api_base: "http://host.docker.internal:11434"
```

- Configure OpenAI LLM.
  - Edit .env file and set your OPENAI_API_KEY

```
      OPENAI_API_KEY="sk-proj-********"
```

- Edit config.yml file - under model_list, add the following lines:

```
      - model_name: openai-gpt-4o
        litellm_params:
          model: "openai/gpt-4o"
          api_key: os.environ/OPENAI_API_KEY
```

--- Create a Custom Guardrail ---

1. Local Guardrail using RegEx

- Change directory to "guardrails/local"
- Create a python program "custom_guardrail_local.py"

2. Guardrail as a Service - using RegEx
3. Guardrail as a Service - using Presidio - runninng in Kubernetes
