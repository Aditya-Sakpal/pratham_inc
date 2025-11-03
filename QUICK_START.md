# ⚡ Quick Start - AWS Lambda Deployment

The fastest way to deploy your FastAPI app to AWS Lambda on Windows.

## 🎯 5-Minute Setup

### 1. Install Prerequisites (One-time)

**Docker Desktop:**
```powershell
# Download and install
# https://www.docker.com/products/docker-desktop
```

**AWS CLI:**
```powershell
# Download and install
# https://awscli.amazonaws.com/AWSCLIV2.msi

# Then configure
aws configure
# Enter your AWS Access Key, Secret Key, region (us-east-1), and format (json)
```

### 2. Create Lambda Execution Role (One-time)

**Easiest way - AWS Console:**
1. Go to: https://console.aws.amazon.com/iam/home#/roles
2. Click **Create role**
3. Select **Lambda** → **Next**
4. Select **AWSLambdaBasicExecutionRole** → **Next** → **Next**
5. Name: `lambda-execution-role`
6. Click **Create role**
7. **Copy the ARN** (you'll need it)

### 3. Deploy!

```powershell
# Run the deployment script
.\deploy_lambda_docker.ps1
```

**When prompted for Role ARN, paste the ARN from step 2.**

### 4. Set Environment Variables

After deployment, copy the Function URL, then run:

```powershell
aws lambda update-function-configuration `
  --function-name ncert-science-platform `
  --environment "Variables={
    OPENAI_API_KEY=sk-your-key-here,
    PINECONE_API_KEY=your-pinecone-key,
    PINECONE_INDEX_NAME=ncert-science,
    PINECONE_NAMESPACE=ncert-books,
    OCR_PROVIDER=openai
  }" `
  --region us-east-1
```

### 5. Test

```powershell
# Replace with your Function URL
curl https://your-url.lambda-url.us-east-1.on.aws/health
```

### 6. Update Frontend

In `frontend/src/App.jsx` or `.env`:
```javascript
const API_BASE_URL = 'https://your-url.lambda-url.us-east-1.on.aws'
```

## 🎉 Done!

Your FastAPI app is now live on AWS Lambda!

---

## 📚 Need More Details?

See `LAMBDA_DOCKER_SETUP.md` for the complete guide with:
- Troubleshooting
- Cost estimates
- Monitoring setup
- Security best practices
- Redeployment instructions

---

## 🆘 Common Issues

**"Docker not found"**
→ Install Docker Desktop and restart

**"AWS credentials not configured"**
→ Run `aws configure`

**"Role not found"**
→ Create the Lambda execution role (Step 2)

**"Function URL not working"**
→ Wait 1-2 minutes after deployment
→ Set environment variables (Step 4)

---

## 💰 Cost

**Free Tier:**
- 1M requests/month forever
- 400,000 GB-seconds/month forever

**After free tier:** ~$1-2/month for moderate use

---

## 🔄 Redeploy After Changes

```powershell
.\deploy_lambda_docker.ps1
```

That's it! The script handles everything.

