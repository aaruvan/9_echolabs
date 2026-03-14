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
