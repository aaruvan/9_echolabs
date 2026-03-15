# Part 2: Cost Comparison and Infrastructure Planning

## Step 2.1: Estimate Token Usage (5 pts)

Average tokens per request = 572

I got this from the project: the local summarization caps input at 512 tokens and outputs up to 60, and the action items call uses around 500 input and 80 output. So 572 is a reasonable average per request.

---

## Step 2.2: Compute Total Token Load (5 pts)

Total Daily Token Load = Daily Active Users × Avg Tokens per Request

| Daily Traffic Category | Daily Active Users | Total Daily Token Load |
|------------------------|--------------------|-------------------------|
| Prototype              | 1,000              | 572,000                 |
| Early Startup          | 10,000             | 5,720,000               |
| Growing Product        | 100,000            | 57,200,000              |
| Large Platform         | 1,000,000          | 572,000,000             |
| Mass Consumer App      | 10,000,000         | 5,720,000,000           |
| Global Platform        | 100,000,000        | 57,200,000,000          |

---

## Step 2.3: Hardware Cost Estimation (Local Hosting) (30 pts)

I assumed a cloud machine with 16-core CPU, GPU, 64 GB RAM at $750/month. Machines needed = ceil(Total Daily Token Load / tokens per machine per day). How many tokens one machine can do per day depends on model size: Ultra-Light about 8M, Small 5M, Medium 2.5M, Large 1M, X-Large 0.4M.

| Model Name | Daily Traffic Category | Avg Tokens per User | Total Daily Token Load | Per Machine Cost (Cloud) | Machines Needed | Total Machine Cost |
|------------|------------------------|---------------------|------------------------|---------------------------|-----------------|---------------------|
| sshleifer/distilbart-cnn-6-6 | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| sshleifer/distilbart-cnn-6-6 | Early Startup | 572 | 5,720,000 | $750/mo | 1 | $750 |
| sshleifer/distilbart-cnn-6-6 | Growing Product | 572 | 57,200,000 | $750/mo | 8 | $6,000 |
| sshleifer/distilbart-cnn-6-6 | Large Platform | 572 | 572,000,000 | $750/mo | 72 | $54,000 |
| sshleifer/distilbart-cnn-6-6 | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 715 | $536,250 |
| sshleifer/distilbart-cnn-6-6 | Global Platform | 572 | 57,200,000,000 | $750/mo | 7,150 | $5,362,500 |
| facebook/bart-large-cnn | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| facebook/bart-large-cnn | Early Startup | 572 | 5,720,000 | $750/mo | 1 | $750 |
| facebook/bart-large-cnn | Growing Product | 572 | 57,200,000 | $750/mo | 8 | $6,000 |
| facebook/bart-large-cnn | Large Platform | 572 | 572,000,000 | $750/mo | 72 | $54,000 |
| facebook/bart-large-cnn | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 715 | $536,250 |
| facebook/bart-large-cnn | Global Platform | 572 | 57,200,000,000 | $750/mo | 7,150 | $5,362,500 |
| google/flan-t5-small | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| google/flan-t5-small | Early Startup | 572 | 5,720,000 | $750/mo | 1 | $750 |
| google/flan-t5-small | Growing Product | 572 | 57,200,000 | $750/mo | 8 | $6,000 |
| google/flan-t5-small | Large Platform | 572 | 572,000,000 | $750/mo | 72 | $54,000 |
| google/flan-t5-small | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 715 | $536,250 |
| google/flan-t5-small | Global Platform | 572 | 57,200,000,000 | $750/mo | 7,150 | $5,362,500 |
| google/flan-t5-base | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| google/flan-t5-base | Early Startup | 572 | 5,720,000 | $750/mo | 2 | $1,500 |
| google/flan-t5-base | Growing Product | 572 | 57,200,000 | $750/mo | 12 | $9,000 |
| google/flan-t5-base | Large Platform | 572 | 572,000,000 | $750/mo | 115 | $86,250 |
| google/flan-t5-base | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 1,144 | $858,000 |
| google/flan-t5-base | Global Platform | 572 | 57,200,000,000 | $750/mo | 11,440 | $8,580,000 |
| facebook/bart-large-xsum | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| facebook/bart-large-xsum | Early Startup | 572 | 5,720,000 | $750/mo | 2 | $1,500 |
| facebook/bart-large-xsum | Growing Product | 572 | 57,200,000 | $750/mo | 12 | $9,000 |
| facebook/bart-large-xsum | Large Platform | 572 | 572,000,000 | $750/mo | 115 | $86,250 |
| facebook/bart-large-xsum | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 1,144 | $858,000 |
| facebook/bart-large-xsum | Global Platform | 572 | 57,200,000,000 | $750/mo | 11,440 | $8,580,000 |
| philschmid/bart-large-cnn-samsum | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| philschmid/bart-large-cnn-samsum | Early Startup | 572 | 5,720,000 | $750/mo | 2 | $1,500 |
| philschmid/bart-large-cnn-samsum | Growing Product | 572 | 57,200,000 | $750/mo | 12 | $9,000 |
| philschmid/bart-large-cnn-samsum | Large Platform | 572 | 572,000,000 | $750/mo | 115 | $86,250 |
| philschmid/bart-large-cnn-samsum | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 1,144 | $858,000 |
| philschmid/bart-large-cnn-samsum | Global Platform | 572 | 57,200,000,000 | $750/mo | 11,440 | $8,580,000 |
| google/flan-t5-large | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| google/flan-t5-large | Early Startup | 572 | 5,720,000 | $750/mo | 3 | $2,250 |
| google/flan-t5-large | Growing Product | 572 | 57,200,000 | $750/mo | 23 | $17,250 |
| google/flan-t5-large | Large Platform | 572 | 572,000,000 | $750/mo | 229 | $171,750 |
| google/flan-t5-large | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 2,288 | $1,716,000 |
| google/flan-t5-large | Global Platform | 572 | 57,200,000,000 | $750/mo | 22,880 | $17,160,000 |
| sshleifer/distilbart-cnn-12-6 | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| sshleifer/distilbart-cnn-12-6 | Early Startup | 572 | 5,720,000 | $750/mo | 3 | $2,250 |
| sshleifer/distilbart-cnn-12-6 | Growing Product | 572 | 57,200,000 | $750/mo | 23 | $17,250 |
| sshleifer/distilbart-cnn-12-6 | Large Platform | 572 | 572,000,000 | $750/mo | 229 | $171,750 |
| sshleifer/distilbart-cnn-12-6 | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 2,288 | $1,716,000 |
| sshleifer/distilbart-cnn-12-6 | Global Platform | 572 | 57,200,000,000 | $750/mo | 22,880 | $17,160,000 |
| facebook/bart-large-mnli | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| facebook/bart-large-mnli | Early Startup | 572 | 5,720,000 | $750/mo | 3 | $2,250 |
| facebook/bart-large-mnli | Growing Product | 572 | 57,200,000 | $750/mo | 23 | $17,250 |
| facebook/bart-large-mnli | Large Platform | 572 | 572,000,000 | $750/mo | 229 | $171,750 |
| facebook/bart-large-mnli | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 2,288 | $1,716,000 |
| facebook/bart-large-mnli | Global Platform | 572 | 57,200,000,000 | $750/mo | 22,880 | $17,160,000 |
| google/flan-t5-xl | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| google/flan-t5-xl | Early Startup | 572 | 5,720,000 | $750/mo | 6 | $4,500 |
| google/flan-t5-xl | Growing Product | 572 | 57,200,000 | $750/mo | 58 | $43,500 |
| google/flan-t5-xl | Large Platform | 572 | 572,000,000 | $750/mo | 572 | $429,000 |
| google/flan-t5-xl | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 5,720 | $4,290,000 |
| google/flan-t5-xl | Global Platform | 572 | 57,200,000,000 | $750/mo | 57,200 | $42,900,000 |
| facebook/bart-large | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| facebook/bart-large | Early Startup | 572 | 5,720,000 | $750/mo | 6 | $4,500 |
| facebook/bart-large | Growing Product | 572 | 57,200,000 | $750/mo | 58 | $43,500 |
| facebook/bart-large | Large Platform | 572 | 572,000,000 | $750/mo | 572 | $429,000 |
| facebook/bart-large | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 5,720 | $4,290,000 |
| facebook/bart-large | Global Platform | 572 | 57,200,000,000 | $750/mo | 57,200 | $42,900,000 |
| google/pegasus-large | Prototype | 572 | 572,000 | $750/mo | 1 | $750 |
| google/pegasus-large | Early Startup | 572 | 5,720,000 | $750/mo | 6 | $4,500 |
| google/pegasus-large | Growing Product | 572 | 57,200,000 | $750/mo | 58 | $43,500 |
| google/pegasus-large | Large Platform | 572 | 572,000,000 | $750/mo | 572 | $429,000 |
| google/pegasus-large | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 5,720 | $4,290,000 |
| google/pegasus-large | Global Platform | 572 | 57,200,000,000 | $750/mo | 57,200 | $42,900,000 |
| google/flan-t5-xxl | Prototype | 572 | 572,000 | $750/mo | 2 | $1,500 |
| google/flan-t5-xxl | Early Startup | 572 | 5,720,000 | $750/mo | 15 | $11,250 |
| google/flan-t5-xxl | Growing Product | 572 | 57,200,000 | $750/mo | 143 | $107,250 |
| google/flan-t5-xxl | Large Platform | 572 | 572,000,000 | $750/mo | 1,430 | $1,072,500 |
| google/flan-t5-xxl | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 14,300 | $10,725,000 |
| google/flan-t5-xxl | Global Platform | 572 | 57,200,000,000 | $750/mo | 143,000 | $107,250,000 |
| google/pegasus-xsum | Prototype | 572 | 572,000 | $750/mo | 2 | $1,500 |
| google/pegasus-xsum | Early Startup | 572 | 5,720,000 | $750/mo | 15 | $11,250 |
| google/pegasus-xsum | Growing Product | 572 | 57,200,000 | $750/mo | 143 | $107,250 |
| google/pegasus-xsum | Large Platform | 572 | 572,000,000 | $750/mo | 1,430 | $1,072,500 |
| google/pegasus-xsum | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 14,300 | $10,725,000 |
| google/pegasus-xsum | Global Platform | 572 | 57,200,000,000 | $750/mo | 143,000 | $107,250,000 |
| allenai/led-large-16384 | Prototype | 572 | 572,000 | $750/mo | 2 | $1,500 |
| allenai/led-large-16384 | Early Startup | 572 | 5,720,000 | $750/mo | 15 | $11,250 |
| allenai/led-large-16384 | Growing Product | 572 | 57,200,000 | $750/mo | 143 | $107,250 |
| allenai/led-large-16384 | Large Platform | 572 | 572,000,000 | $750/mo | 1,430 | $1,072,500 |
| allenai/led-large-16384 | Mass Consumer App | 572 | 5,720,000,000 | $750/mo | 14,300 | $10,725,000 |
| allenai/led-large-16384 | Global Platform | 572 | 57,200,000,000 | $750/mo | 143,000 | $107,250,000 |

---

## Step 2.4: Hugging Face Inference API Cost Comparison (30 pts)

For the comparable model I used the same model on Hugging Face. Cost per token is tiered by size (smaller models cheaper). Monthly API cost = Total Daily Token Load × 30 × cost per token. I added one app server at $150/mo for the API setup.

| Local LLM Model | Comparable HF Model | Cost per Token | Daily Traffic Category | Total Token Load | Est. API Cost (mo) | Machines (API infra) | Total Cost |
|-----------------|----------------------|----------------|------------------------|------------------|--------------------|------------------------|------------|
| sshleifer/distilbart-cnn-6-6 | (same) | $0.00002 | Prototype | 572,000 | $343 | 1 | $493 |
| sshleifer/distilbart-cnn-6-6 | (same) | $0.00002 | Early Startup | 5,720,000 | $3,432 | 1 | $3,582 |
| sshleifer/distilbart-cnn-6-6 | (same) | $0.00002 | Growing Product | 57,200,000 | $34,320 | 1 | $34,470 |
| sshleifer/distilbart-cnn-6-6 | (same) | $0.00002 | Large Platform | 572,000,000 | $343,200 | 2 | $343,350 |
| sshleifer/distilbart-cnn-6-6 | (same) | $0.00002 | Mass Consumer App | 5,720,000,000 | $3,432,000 | 5 | $3,432,750 |
| sshleifer/distilbart-cnn-6-6 | (same) | $0.00002 | Global Platform | 57,200,000,000 | $34,320,000 | 20 | $34,323,000 |
| facebook/bart-large-cnn | (same) | $0.00002 | Prototype | 572,000 | $343 | 1 | $493 |
| facebook/bart-large-cnn | (same) | $0.00002 | Early Startup | 5,720,000 | $3,432 | 1 | $3,582 |
| facebook/bart-large-cnn | (same) | $0.00002 | Growing Product | 57,200,000 | $34,320 | 1 | $34,470 |
| facebook/bart-large-cnn | (same) | $0.00002 | Large Platform | 572,000,000 | $343,200 | 2 | $343,350 |
| facebook/bart-large-cnn | (same) | $0.00002 | Mass Consumer App | 5,720,000,000 | $3,432,000 | 5 | $3,432,750 |
| facebook/bart-large-cnn | (same) | $0.00002 | Global Platform | 57,200,000,000 | $34,320,000 | 20 | $34,323,000 |
| google/flan-t5-small | (same) | $0.00002 | Prototype | 572,000 | $343 | 1 | $493 |
| google/flan-t5-small | (same) | $0.00002 | Early Startup | 5,720,000 | $3,432 | 1 | $3,582 |
| google/flan-t5-small | (same) | $0.00002 | Growing Product | 57,200,000 | $34,320 | 1 | $34,470 |
| google/flan-t5-small | (same) | $0.00002 | Large Platform | 572,000,000 | $343,200 | 2 | $343,350 |
| google/flan-t5-small | (same) | $0.00002 | Mass Consumer App | 5,720,000,000 | $3,432,000 | 5 | $3,432,750 |
| google/flan-t5-small | (same) | $0.00002 | Global Platform | 57,200,000,000 | $34,320,000 | 20 | $34,323,000 |
| google/flan-t5-base | (same) | $0.00002 | Prototype | 572,000 | $343 | 1 | $493 |
| google/flan-t5-base | (same) | $0.00002 | Early Startup | 5,720,000 | $3,432 | 1 | $3,582 |
| google/flan-t5-base | (same) | $0.00002 | Growing Product | 57,200,000 | $34,320 | 1 | $34,470 |
| google/flan-t5-base | (same) | $0.00002 | Large Platform | 572,000,000 | $343,200 | 2 | $343,350 |
| google/flan-t5-base | (same) | $0.00002 | Mass Consumer App | 5,720,000,000 | $3,432,000 | 5 | $3,432,750 |
| google/flan-t5-base | (same) | $0.00002 | Global Platform | 57,200,000,000 | $34,320,000 | 20 | $34,323,000 |
| facebook/bart-large-xsum | (same) | $0.00002 | Prototype | 572,000 | $343 | 1 | $493 |
| facebook/bart-large-xsum | (same) | $0.00002 | Early Startup | 5,720,000 | $3,432 | 1 | $3,582 |
| facebook/bart-large-xsum | (same) | $0.00002 | Growing Product | 57,200,000 | $34,320 | 1 | $34,470 |
| facebook/bart-large-xsum | (same) | $0.00002 | Large Platform | 572,000,000 | $343,200 | 2 | $343,350 |
| facebook/bart-large-xsum | (same) | $0.00002 | Mass Consumer App | 5,720,000,000 | $3,432,000 | 5 | $3,432,750 |
| facebook/bart-large-xsum | (same) | $0.00002 | Global Platform | 57,200,000,000 | $34,320,000 | 20 | $34,323,000 |
| philschmid/bart-large-cnn-samsum | (same) | $0.00002 | Prototype | 572,000 | $343 | 1 | $493 |
| philschmid/bart-large-cnn-samsum | (same) | $0.00002 | Early Startup | 5,720,000 | $3,432 | 1 | $3,582 |
| philschmid/bart-large-cnn-samsum | (same) | $0.00002 | Growing Product | 57,200,000 | $34,320 | 1 | $34,470 |
| philschmid/bart-large-cnn-samsum | (same) | $0.00002 | Large Platform | 572,000,000 | $343,200 | 2 | $343,350 |
| philschmid/bart-large-cnn-samsum | (same) | $0.00002 | Mass Consumer App | 5,720,000,000 | $3,432,000 | 5 | $3,432,750 |
| philschmid/bart-large-cnn-samsum | (same) | $0.00002 | Global Platform | 57,200,000,000 | $34,320,000 | 20 | $34,323,000 |
| google/flan-t5-large | (same) | $0.00004 | Prototype | 572,000 | $686 | 1 | $836 |
| google/flan-t5-large | (same) | $0.00004 | Early Startup | 5,720,000 | $6,864 | 1 | $7,014 |
| google/flan-t5-large | (same) | $0.00004 | Growing Product | 57,200,000 | $68,640 | 1 | $68,790 |
| google/flan-t5-large | (same) | $0.00004 | Large Platform | 572,000,000 | $686,400 | 2 | $686,550 |
| google/flan-t5-large | (same) | $0.00004 | Mass Consumer App | 5,720,000,000 | $6,864,000 | 5 | $6,864,750 |
| google/flan-t5-large | (same) | $0.00004 | Global Platform | 57,200,000,000 | $68,640,000 | 20 | $68,643,000 |
| sshleifer/distilbart-cnn-12-6 | (same) | $0.00004 | Prototype | 572,000 | $686 | 1 | $836 |
| sshleifer/distilbart-cnn-12-6 | (same) | $0.00004 | Early Startup | 5,720,000 | $6,864 | 1 | $7,014 |
| sshleifer/distilbart-cnn-12-6 | (same) | $0.00004 | Growing Product | 57,200,000 | $68,640 | 1 | $68,790 |
| sshleifer/distilbart-cnn-12-6 | (same) | $0.00004 | Large Platform | 572,000,000 | $686,400 | 2 | $686,550 |
| sshleifer/distilbart-cnn-12-6 | (same) | $0.00004 | Mass Consumer App | 5,720,000,000 | $6,864,000 | 5 | $6,864,750 |
| sshleifer/distilbart-cnn-12-6 | (same) | $0.00004 | Global Platform | 57,200,000,000 | $68,640,000 | 20 | $68,643,000 |
| facebook/bart-large-mnli | (same) | $0.00004 | Prototype | 572,000 | $686 | 1 | $836 |
| facebook/bart-large-mnli | (same) | $0.00004 | Early Startup | 5,720,000 | $6,864 | 1 | $7,014 |
| facebook/bart-large-mnli | (same) | $0.00004 | Growing Product | 57,200,000 | $68,640 | 1 | $68,790 |
| facebook/bart-large-mnli | (same) | $0.00004 | Large Platform | 572,000,000 | $686,400 | 2 | $686,550 |
| facebook/bart-large-mnli | (same) | $0.00004 | Mass Consumer App | 5,720,000,000 | $6,864,000 | 5 | $6,864,750 |
| facebook/bart-large-mnli | (same) | $0.00004 | Global Platform | 57,200,000,000 | $68,640,000 | 20 | $68,643,000 |
| google/flan-t5-xl | (same) | $0.00008 | Prototype | 572,000 | $1,373 | 1 | $1,523 |
| google/flan-t5-xl | (same) | $0.00008 | Early Startup | 5,720,000 | $13,728 | 1 | $13,878 |
| google/flan-t5-xl | (same) | $0.00008 | Growing Product | 57,200,000 | $137,280 | 1 | $137,430 |
| google/flan-t5-xl | (same) | $0.00008 | Large Platform | 572,000,000 | $1,372,800 | 2 | $1,372,950 |
| google/flan-t5-xl | (same) | $0.00008 | Mass Consumer App | 5,720,000,000 | $13,728,000 | 5 | $13,728,750 |
| google/flan-t5-xl | (same) | $0.00008 | Global Platform | 57,200,000,000 | $137,280,000 | 20 | $137,283,000 |
| facebook/bart-large | (same) | $0.00008 | Prototype | 572,000 | $1,373 | 1 | $1,523 |
| facebook/bart-large | (same) | $0.00008 | Early Startup | 5,720,000 | $13,728 | 1 | $13,878 |
| facebook/bart-large | (same) | $0.00008 | Growing Product | 57,200,000 | $137,280 | 1 | $137,430 |
| facebook/bart-large | (same) | $0.00008 | Large Platform | 572,000,000 | $1,372,800 | 2 | $1,372,950 |
| facebook/bart-large | (same) | $0.00008 | Mass Consumer App | 5,720,000,000 | $13,728,000 | 5 | $13,728,750 |
| facebook/bart-large | (same) | $0.00008 | Global Platform | 57,200,000,000 | $137,280,000 | 20 | $137,283,000 |
| google/pegasus-large | (same) | $0.00008 | Prototype | 572,000 | $1,373 | 1 | $1,523 |
| google/pegasus-large | (same) | $0.00008 | Early Startup | 5,720,000 | $13,728 | 1 | $13,878 |
| google/pegasus-large | (same) | $0.00008 | Growing Product | 57,200,000 | $137,280 | 1 | $137,430 |
| google/pegasus-large | (same) | $0.00008 | Large Platform | 572,000,000 | $1,372,800 | 2 | $1,372,950 |
| google/pegasus-large | (same) | $0.00008 | Mass Consumer App | 5,720,000,000 | $13,728,000 | 5 | $13,728,750 |
| google/pegasus-large | (same) | $0.00008 | Global Platform | 57,200,000,000 | $137,280,000 | 20 | $137,283,000 |
| google/flan-t5-xxl | (same) | $0.00015 | Prototype | 572,000 | $2,574 | 1 | $2,724 |
| google/flan-t5-xxl | (same) | $0.00015 | Early Startup | 5,720,000 | $25,740 | 1 | $25,890 |
| google/flan-t5-xxl | (same) | $0.00015 | Growing Product | 57,200,000 | $257,400 | 1 | $257,550 |
| google/flan-t5-xxl | (same) | $0.00015 | Large Platform | 572,000,000 | $2,574,000 | 2 | $2,574,150 |
| google/flan-t5-xxl | (same) | $0.00015 | Mass Consumer App | 5,720,000,000 | $25,740,000 | 5 | $25,740,750 |
| google/flan-t5-xxl | (same) | $0.00015 | Global Platform | 57,200,000,000 | $257,400,000 | 20 | $257,403,000 |
| google/pegasus-xsum | (same) | $0.00015 | Prototype | 572,000 | $2,574 | 1 | $2,724 |
| google/pegasus-xsum | (same) | $0.00015 | Early Startup | 5,720,000 | $25,740 | 1 | $25,890 |
| google/pegasus-xsum | (same) | $0.00015 | Growing Product | 57,200,000 | $257,400 | 1 | $257,550 |
| google/pegasus-xsum | (same) | $0.00015 | Large Platform | 572,000,000 | $2,574,000 | 2 | $2,574,150 |
| google/pegasus-xsum | (same) | $0.00015 | Mass Consumer App | 5,720,000,000 | $25,740,000 | 5 | $25,740,750 |
| google/pegasus-xsum | (same) | $0.00015 | Global Platform | 57,200,000,000 | $257,400,000 | 20 | $257,403,000 |
| allenai/led-large-16384 | (same) | $0.00015 | Prototype | 572,000 | $2,574 | 1 | $2,724 |
| allenai/led-large-16384 | (same) | $0.00015 | Early Startup | 5,720,000 | $25,740 | 1 | $25,890 |
| allenai/led-large-16384 | (same) | $0.00015 | Growing Product | 57,200,000 | $257,400 | 1 | $257,550 |
| allenai/led-large-16384 | (same) | $0.00015 | Large Platform | 572,000,000 | $2,574,000 | 2 | $2,574,150 |
| allenai/led-large-16384 | (same) | $0.00015 | Mass Consumer App | 5,720,000,000 | $25,740,000 | 5 | $25,740,750 |
| allenai/led-large-16384 | (same) | $0.00015 | Global Platform | 57,200,000,000 | $257,400,000 | 20 | $257,403,000 |

Comparison for philschmid/bart-large-cnn-samsum (small model):

| Traffic Category | Local Hosting Cost | API Total Cost | Cheaper |
|-----------------|--------------------|----------------|---------|
| Prototype | $750 | $493 | API |
| Early Startup | $1,500 | $3,582 | Local |
| Growing Product | $9,000 | $34,470 | Local |
| Large Platform | $86,250 | $343,350 | Local |
| Mass Consumer App | $858,000 | $3,432,750 | Local |
| Global Platform | $8,580,000 | $34,323,000 | Local |

You always pay for at least one machine with local ($750), so at really low volume the API wins. Once traffic is high enough that you need more than one machine anyway, local ends up cheaper per token.

---

## Step 2.5: Analysis (30 pts)

Local hosting is cheaper once you have enough traffic that the fixed machine cost spreads out. In these numbers that’s around Early Startup (10K DAU) for small models—one machine can handle it and the API bill would already be higher than $750/mo. For bigger models the crossover is later, around Growing Product or more, when you’d need a lot of machines and the per-token API cost adds up.

API is cheaper when traffic is low or uneven, like Prototype (1K DAU) and sometimes Early Startup. You only pay for what you use, so until you’re doing something like 5–10M tokens per day (depends on model and rates), the API stays under what you’d pay for one machine plus ops.

I’d start with the API or a hybrid (like Echolabs: summary local, action items via HF). When usage gets steady and the monthly API cost clearly beats the cost of running your own machines, move more workload local. A hybrid—local for the heavy summarization, API for action items or spikes—works well and you can re-check the numbers as traffic and pricing change.

---

# Part 3: Multi-Model Routing Strategy (50 pts)

## Step 3.1: Define Five System Scenarios (15 pts)

Five realistic situations where routing decisions matter for Echolabs (conversation summarization + action items):

| Scenario | Description |
|----------|-------------|
| **Normal operation** | Standard traffic: users open conversation detail, request summary and/or action items. Load is predictable, latency budget ~5–10s acceptable. |
| **Peak usage hours** | Sudden spikes (e.g. morning standup time, end-of-day review). Queue depth grows; local model can become a bottleneck; we want to avoid timeouts and dropped requests. |
| **Long or complex transcripts** | User has a conversation with many segments or very long text. Risk of truncation, slower inference, or lower summary quality. Needs a model that handles long context or we preprocess aggressively. |
| **Cost optimization** | We want to minimize API spend and machine cost. Prefer local for high-volume summarization; use API only when necessary (e.g. action items, or fallback when local is overloaded). |
| **System overload** | CPU/memory pressure from many concurrent requests; local model is slow or failing. We need to shed load or route to an external API so the app stays responsive and doesn't crash. |

---

## Step 3.2: Design Routing Strategies (15 pts)

| Scenario | Routing Strategy | Local Models Used | Hugging Face Model Used | Expected Benefit |
|----------|------------------|-------------------|--------------------------|------------------|
| **Normal operation** | Route all summary requests to local BART (bart-large-cnn-samsum). Route action-items requests to HF Inference API (e.g. flan-t5-base). No conditional switching. | philschmid/bart-large-cnn-samsum | google/flan-t5-base (Inference API) for action items | Predictable cost, good quality; data stays on our server for summaries. |
| **Peak usage hours** | Route short/simple transcripts (e.g. &lt; 5 segments or &lt; 500 tokens) to a faster local model (distilbart-cnn-12-6). Route longer or "premium" requests to primary BART or to HF API to avoid queue buildup. Optionally cap queue and return "try again later" or route overflow to API. | distilbart-cnn-12-6 (simple), bart-large-cnn-samsum (default) | Same HF model for action items; optionally use HF for summary overflow | Lower p95 latency during peaks; fewer timeouts; API absorbs spikes. |
| **Long or complex transcripts** | If transcript length &gt; threshold (e.g. 1500 chars), first compress with local small model (distilbart) or truncate, then send to primary BART for summary. Action items: send truncated or summarized text to API to reduce tokens and cost. | distilbart-cnn-12-6 (pre-summary), bart-large-cnn-samsum (main summary) | flan-t5-base for action items (input = summary or truncated transcript) | Keeps latency and token usage bounded; maintains acceptable quality on long inputs. |
| **Cost optimization** | Always prefer local for summarization (no per-token). Use API only for action items. If daily request volume is low, consider routing some summaries to API to avoid keeping a large local machine running 24/7. | bart-large-cnn-samsum (primary); optionally distilbart for low-priority or batch jobs | flan-t5-base only for action items (or summary if we temporarily scale down local) | Minimizes API spend; fixed local cost dominates only at sufficient volume. |
| **System overload** | If local inference latency &gt; threshold (e.g. 15s) or error rate spikes, temporarily route new summary requests to HF Inference API (same or comparable model). Revert to local when health check recovers. Action items stay on API. | bart-large-cnn-samsum when healthy | HF Inference for summary (fallback) + action items | Prevents cascading failures; keeps UX acceptable; we pay more during overload but avoid downtime. |

---

## Step 3.3: Evaluate the Strategy (20 pts)

**How the strategy improves latency**

- **Normal operation:** Single path (local summary, API action items) keeps design simple and avoids extra condition checks, so latency is just model inference + one API call for action items. No added routing delay.
- **Peak usage:** Routing simple requests to a faster local model (distilbart) reduces average time per request and shortens the queue. Sending overflow to the API avoids long waits on the local worker; users get a response instead of a timeout. Overall p95 latency goes down during spikes.
- **Long transcripts:** Pre-compressing or truncating with a small local model (or rules) before the main BART call keeps input size and inference time bounded. Sending a shorter text to the API for action items also reduces API latency and avoids token limits. End-to-end latency stays within a predictable range instead of growing with transcript length.
- **Cost optimization:** Routing doesn't add latency; it only affects which backend handles the request. Preferring local for summaries keeps response time tied to our own infra (no extra network hop to API for that step).
- **System overload:** Failing over to the API when local is slow or failing prevents requests from piling up on a stuck local model. Users get answers from the API (possibly slightly higher latency) instead of long spins or errors. Recovery to local when healthy restores baseline latency.

**How it reduces cost**

- **Normal operation:** Most tokens are generated locally (summary), so we pay only for action-items API calls. Cost is dominated by one machine + limited API usage.
- **Peak usage:** Using a smaller/faster local model for simple cases reduces the need to add more machines or to send every request to the API. Overflow to API is paid per request but only when necessary, so we avoid over-provisioning for rare peaks.
- **Long transcripts:** Sending a compressed or truncated input to the API for action items reduces input (and often output) tokens, so per-request API cost is lower. Local preprocessing is free (we already run the server).
- **Cost optimization:** Explicit "prefer local for summarization" and "API only for action items" keeps API spend minimal. Optional "route some work to API when volume is low" lets us scale down or shut off the local machine in quiet periods instead of paying 24/7 for low utilization.
- **System overload:** Fallback to API during overload increases cost only during the incident. We avoid the larger cost of adding extra machines just to handle rare spikes, and we avoid lost revenue or SLA penalties from outages.

**How it maintains output quality**

- **Normal operation:** We use the same models we validated in the notebook (BART for summary, flan-t5 for action items), so quality matches our benchmarks. No dilution from unnecessary model switching.
- **Peak usage:** The faster local model is used only for "simple" transcripts (short, few segments); we define "simple" so that distilbart's lower quality is acceptable for those cases. Complex or long transcripts still get the primary BART or API, so quality stays high where it matters.
- **Long transcripts:** Preprocessing (truncate or compress) is chosen so that the main summary model still receives the most important content (e.g. first + last segments, or a first-pass summary). Action items are generated from that same reduced input, so we don't lose key information and quality remains good.
- **Cost optimization:** Routing is by volume and feature (local vs API), not by downgrading model quality. We might route more to API when scaling down local, but we use a comparable HF model so quality doesn't drop.
- **System overload:** Fallback to the API uses a comparable or same model (e.g. BART or equivalent on HF Inference), so summary quality during overload is similar to local. Action items continue to use the same API model, so quality is unchanged. The only tradeoff is higher cost during the incident, not lower quality.
