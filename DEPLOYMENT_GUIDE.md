# Deployment Guide - Free Cloud Hosting

This guide covers deploying your Budget app to free cloud hosting services.

## 🐳 Docker Deployment (Recommended)

**Your app is already containerized!** You can deploy the Docker container directly to several platforms without any changes.

### Docker-Supported Platforms

#### 1. **Railway** (Recommended - Easiest Docker Deployment)
- **Free Tier**: $5/month credit (usually enough for small apps)
- **Docker Support**: ✅ Full Docker support
- **Pros**: Easy deployment, automatic HTTPS, PostgreSQL included, detects Dockerfile automatically
- **Cons**: Requires credit card (but won't charge if under limit)
- **Best for**: Modern deployment experience

#### 2. **Render**
- **Free Tier**: Free web service (spins down after 15 min inactivity)
- **Docker Support**: ✅ Full Docker support
- **Pros**: Free PostgreSQL, easy setup, Dockerfile support
- **Cons**: Cold starts after inactivity (first request is slow)
- **Best for**: Development/testing, low-traffic apps

#### 3. **Fly.io**
- **Free Tier**: 3 shared-cpu VMs, 3GB persistent volumes
- **Docker Support**: ✅ Full Docker support
- **Pros**: Always-on free tier, global edge network
- **Cons**: More complex setup
- **Best for**: Always-on free hosting

#### 4. **Google Cloud Run**
- **Free Tier**: 2 million requests/month, 360,000 GB-seconds
- **Docker Support**: ✅ Full Docker support
- **Pros**: Generous free tier, auto-scaling
- **Cons**: Requires Google Cloud account
- **Best for**: High-traffic apps

## 🚀 Quick Start: Deploy Docker Container to Railway

### Step 1: Prepare Your Code

1. **Create a GitHub repository** (if you haven't already):
   ```bash
   git init
   git add .
   git commit -m "Ready for Docker deployment"
   git remote add origin https://github.com/yourusername/budget-app.git
   git push -u origin main
   ```

2. **Your Dockerfile is already configured!** It will:
   - Use Python 3.11
   - Install all dependencies
   - Collect static files
   - Run with Gunicorn
   - Use PORT environment variable (Railway provides this automatically)

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app) and sign up (GitHub login works)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. **Railway will automatically detect your Dockerfile and deploy it!**
5. Add environment variables in Railway dashboard:
   - `SECRET_KEY` - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app-name.railway.app`
6. Add a PostgreSQL database (Railway will provide `DATABASE_URL` automatically)
7. Your app will be live at `https://your-app-name.railway.app`

**That's it!** Railway handles everything - no Procfile or runtime.txt needed when using Docker.

### Step 3: Run Migrations

Railway will run migrations automatically, but you can also run manually:
```bash
railway run python manage.py migrate
```

### Step 4: Create Superuser

```bash
railway run python manage.py createsuperuser
```

## 🐳 Deploy Docker Container to Render

### Step 1: Deploy to Render

1. Go to [render.com](https://render.com) and sign up
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. **Select "Docker" as the environment** (Render will detect your Dockerfile)
5. Render will automatically:
   - Build your Docker image
   - Deploy it
   - Provide a URL
6. Add environment variables:
   - `SECRET_KEY` - Generate a new secret key
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app-name.onrender.com`
7. Add PostgreSQL database (free tier available)
8. Deploy!

**Note**: Free tier spins down after 15 minutes of inactivity. First request after spin-down takes ~30 seconds.

## 🐳 Deploy Docker Container to Fly.io

### Step 1: Install Fly CLI
```bash
# macOS
brew install flyctl

# Or download from https://fly.io/docs/getting-started/installing-flyctl/
```

### Step 2: Create Fly.io App
```bash
fly auth login
fly launch
```

Fly.io will:
- Detect your Dockerfile
- Ask a few questions
- Deploy your app

### Step 3: Add PostgreSQL
```bash
fly postgres create --name budget-db
fly postgres attach budget-db
```

### Step 4: Set Environment Variables
```bash
fly secrets set SECRET_KEY=your-secret-key
fly secrets set DEBUG=False
fly secrets set ALLOWED_HOSTS=your-app-name.fly.dev
```

Your app will be live at `https://your-app-name.fly.dev`

## 🐳 Deploy Docker Container to Google Cloud Run

Google Cloud Run is a serverless platform that automatically scales your containers. It offers a generous free tier and supports Docker deployments.

### Step 1: Prerequisites

1. **Google Cloud Account** - Sign up at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud SDK (gcloud)** - Install the CLI tool
3. **Enable Billing** - Free tier requires a credit card (but you won't be charged for free tier usage)

### Step 2: Install Google Cloud SDK

**macOS:**
```bash
# Download and install
curl https://sdk.cloud.google.com | bash

# Restart your shell or run:
exec -l $SHELL

# Initialize
gcloud init
```

**Or use Homebrew:**
```bash
brew install --cask google-cloud-sdk
gcloud init
```

### Step 3: Set Up Your Project

1. **Create a new project** (or use existing):
   ```bash
   gcloud projects create budget-app --name="Budget App"
   gcloud config set project budget-app
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   ```

3. **Set your region**:
   ```bash
   gcloud config set compute/region us-central1  # or your preferred region
   ```

### Step 4: Set Up Cloud SQL (PostgreSQL)

1. **Create a Cloud SQL instance**:
   ```bash
   gcloud sql instances create budget-db \
     --database-version=POSTGRES_15 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

   **Note**: `db-f1-micro` is the smallest (free tier eligible) instance.

2. **Create a database**:
   ```bash
   gcloud sql databases create budgetdb --instance=budget-db
   ```

3. **Create a database user**:
   ```bash
   gcloud sql users create budgetuser \
     --instance=budget-db \
     --password=YOUR_SECURE_PASSWORD
   ```

4. **Get the connection name** (you'll need this):
   ```bash
   gcloud sql instances describe budget-db --format="value(connectionName)"
   ```
   Example output: `budget-app:us-central1:budget-db`

### Step 5: Build and Push Docker Image

1. **Authenticate Docker with Google Cloud**:
   ```bash
   gcloud auth configure-docker
   ```

2. **Set your project ID**:
   ```bash
   export PROJECT_ID=$(gcloud config get-value project)
   ```

3. **Build the Docker image**:
   ```bash
   cd /Users/gert/projects/Budget
   gcloud builds submit --tag gcr.io/$PROJECT_ID/budget-app
   ```

   This will:
   - Build your Docker image using Cloud Build
   - Push it to Google Container Registry
   - Take a few minutes the first time

### Step 6: Deploy to Cloud Run

1. **Get your Cloud SQL connection name**:
   ```bash
   export CONNECTION_NAME=$(gcloud sql instances describe budget-db --format="value(connectionName)")
   ```

2. **Deploy your service**:
   ```bash
   gcloud run deploy budget-app \
     --image gcr.io/$PROJECT_ID/budget-app \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --add-cloudsql-instances $CONNECTION_NAME \
     --set-env-vars "SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" \
     --set-env-vars "DEBUG=False"
   ```

3. **Note the service URL** - Cloud Run will provide a URL like:
   `https://budget-app-xxxxx-uc.a.run.app`

4. **Update ALLOWED_HOSTS** with your actual URL:
   ```bash
   gcloud run services update budget-app \
     --region us-central1 \
     --update-env-vars "ALLOWED_HOSTS=your-actual-url.run.app"
   ```

### Step 7: Configure Database Connection

1. **Construct your DATABASE_URL**:
   ```
   postgresql://budgetuser:YOUR_PASSWORD@/budgetdb?host=/cloudsql/budget-app:us-central1:budget-db
   ```

2. **Update your service with DATABASE_URL**:
   ```bash
   gcloud run services update budget-app \
     --region us-central1 \
     --update-env-vars "DATABASE_URL=postgresql://budgetuser:YOUR_PASSWORD@/budgetdb?host=/cloudsql/$CONNECTION_NAME"
   ```

   **Important**: Replace `YOUR_PASSWORD` with the password you set in Step 4.

### Step 8: Run Database Migrations

1. **Create a Cloud Run job for migrations** (one-time):
   ```bash
   gcloud run jobs create budget-migrate \
     --image gcr.io/$PROJECT_ID/budget-app \
     --region us-central1 \
     --add-cloudsql-instances $CONNECTION_NAME \
     --set-env-vars "DATABASE_URL=postgresql://budgetuser:YOUR_PASSWORD@/budgetdb?host=/cloudsql/$CONNECTION_NAME" \
     --command python \
     --args manage.py,migrate
   ```

2. **Execute the migration job**:
   ```bash
   gcloud run jobs execute budget-migrate --region us-central1
   ```

3. **Create superuser** (use Cloud Shell or local connection):
   ```bash
   # Option 1: Use Cloud Shell in Google Cloud Console
   # Connect to your database and run:
   python manage.py createsuperuser
   
   # Option 2: Use Cloud Run job (interactive)
   gcloud run jobs create budget-createsuperuser \
     --image gcr.io/$PROJECT_ID/budget-app \
     --region us-central1 \
     --add-cloudsql-instances $CONNECTION_NAME \
     --set-env-vars "DATABASE_URL=postgresql://budgetuser:YOUR_PASSWORD@/budgetdb?host=/cloudsql/$CONNECTION_NAME" \
     --command python \
     --args manage.py,createsuperuser
   ```

### Step 9: Verify Deployment

1. Visit your Cloud Run service URL
2. You should see the login page
3. Log in with your superuser credentials
4. Test the app functionality

### Google Cloud Run Features

- ✅ **Automatic HTTPS** - SSL certificate provided automatically
- ✅ **Auto-scaling** - Scales to zero when not in use (free tier)
- ✅ **Pay per use** - Only pay for requests and compute time
- ✅ **Custom domains** - Add your own domain
- ✅ **Logs** - Integrated with Cloud Logging
- ✅ **Monitoring** - Built-in metrics and alerts

### Google Cloud Free Tier

**Always Free (per month):**
- ✅ **2 million requests**
- ✅ **360,000 GB-seconds** of compute time
- ✅ **180,000 vCPU-seconds**
- ✅ **1 GB egress** (outbound data transfer)

**Cloud SQL Free Tier:**
- ✅ **db-f1-micro** instance eligible for free tier
- ✅ **First 1 GB storage** free per month
- ⚠️ **Requires billing account** (but won't charge for free tier usage)

### Google Cloud Pricing

- **Cloud Run**: Pay only for what you use beyond free tier
- **Cloud SQL**: Free tier covers small instances, then ~$7-10/month for db-f1-micro
- **Cloud Build**: 120 build-minutes/day free
- **Container Registry**: 0.5 GB storage free, then $0.026/GB/month

**Estimated monthly cost for small app**: $0-10 (usually stays within free tier)

### Google Cloud Run Limitations

- ⚠️ **Cold starts** - First request after inactivity takes ~5-10 seconds
- ⚠️ **Request timeout** - Maximum 60 minutes per request
- ⚠️ **Memory limits** - Up to 8 GB per instance
- ⚠️ **Concurrent requests** - Up to 80 per instance (default)

### Custom Domain Setup

1. **Map a custom domain**:
   ```bash
   gcloud run domain-mappings create \
     --service budget-app \
     --domain your-domain.com \
     --region us-central1
   ```

2. **Follow DNS instructions** - Google will provide DNS records to add

3. **Verify domain ownership** in Google Search Console

### Continuous Deployment with Cloud Build

1. **Create `cloudbuild.yaml`** in your project root:
   ```yaml
   steps:
     # Build the container image
     - name: 'gcr.io/cloud-builders/docker'
       args: ['build', '-t', 'gcr.io/$PROJECT_ID/budget-app', '.']
     
     # Push the container image
     - name: 'gcr.io/cloud-builders/docker'
       args: ['push', 'gcr.io/$PROJECT_ID/budget-app']
     
     # Deploy container image to Cloud Run
     - name: 'gcr.io/cloud-builders/gcloud'
       args:
         - 'run'
         - 'deploy'
         - 'budget-app'
         - '--image'
         - 'gcr.io/$PROJECT_ID/budget-app'
         - '--region'
         - 'us-central1'
         - '--platform'
         - 'managed'
   ```

2. **Connect GitHub repository**:
   - Go to Cloud Build → Triggers
   - Click "Create Trigger"
   - Connect your GitHub repository
   - Set trigger to push to `main` branch
   - Use `cloudbuild.yaml` as the configuration file

3. **Automatic deployments** - Every push to `main` will trigger a build and deploy

### Troubleshooting Google Cloud Run

**Service won't start:**
- Check logs: `gcloud run services logs read budget-app --region us-central1`
- Verify environment variables are set correctly
- Check Cloud SQL connection name format

**Database connection errors:**
- Verify Cloud SQL instance is running: `gcloud sql instances describe budget-db`
- Check `--add-cloudsql-instances` flag includes correct connection name
- Verify database user and password are correct

**Build fails:**
- Check Cloud Build logs in Google Cloud Console
- Verify `requirements.txt` is up to date
- Check Dockerfile syntax

**High costs:**
- Review Cloud Run metrics in console
- Set concurrency limits to reduce instances
- Use Cloud Run's min-instances=0 to scale to zero

### Google Cloud Run Commands Reference

```bash
# View service details
gcloud run services describe budget-app --region us-central1

# View logs
gcloud run services logs read budget-app --region us-central1 --limit 50

# Update environment variables
gcloud run services update budget-app \
  --region us-central1 \
  --update-env-vars KEY=value

# Update service with new image
gcloud run deploy budget-app \
  --image gcr.io/$PROJECT_ID/budget-app \
  --region us-central1

# Delete service
gcloud run services delete budget-app --region us-central1

# List all services
gcloud run services list --region us-central1
```

## 📝 Non-Docker Deployment Options

### PythonAnywhere
- **Free Tier**: Limited but always-on
- **Docker Support**: ❌ No Docker support
- **Pros**: No credit card needed, always-on
- **Cons**: Limited external requests, single web app, manual setup
- **Best for**: Simple deployment, learning

See the original deployment guide sections below for PythonAnywhere instructions.

## Environment Variables

For production, set these environment variables:

```bash
SECRET_KEY=your-secret-key-here  # Generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

## Database Migration (SQLite → PostgreSQL)

If you want to migrate from SQLite to PostgreSQL:

1. **Export data from SQLite** (before deploying):
   ```bash
   python manage.py dumpdata > data.json
   ```

2. **Deploy to Railway/Render/Google Cloud Run** (they provide PostgreSQL automatically via `DATABASE_URL`)

3. **Run migrations**:
   ```bash
   railway run python manage.py migrate
   # or on Render: render run python manage.py migrate
   ```

4. **Import data**:
   ```bash
   railway run python manage.py loaddata data.json
   ```

## Static Files

Static files are configured to be served via WhiteNoise (included in requirements). The Dockerfile automatically runs `collectstatic` during build. For production:
- Railway/Render: Automatic via Dockerfile
- Fly.io: Automatic via Dockerfile
- Google Cloud Run: Automatic via Dockerfile

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Generate new `SECRET_KEY` (don't use the one in settings.py)
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Use HTTPS (Railway/Render/Fly.io/Google Cloud Run provide automatically)
- [ ] Use PostgreSQL instead of SQLite for production (Railway/Render/Google Cloud Run provide this)

## Troubleshooting

### Database Issues
- If using SQLite: Make sure the database file is writable (not recommended for production)
- If using PostgreSQL: Check `DATABASE_URL` environment variable is set

### Static Files Not Loading
- The Dockerfile runs `collectstatic` automatically
- Check `STATIC_URL` and `STATIC_ROOT` in settings
- WhiteNoise middleware is configured in settings

### 500 Errors
- Check logs in Railway/Render/Fly.io/Google Cloud Run dashboard
- Set `DEBUG=True` temporarily to see error details (remember to set back to False!)
- Check environment variables are set correctly

### Docker Build Fails
- Check that all files are committed to Git
- Verify `requirements.txt` is up to date
- Check `.dockerignore` isn't excluding necessary files

## Cost Comparison

| Service | Free Tier | Docker Support | Limitations |
|---------|----------|----------------|-------------|
| Railway | $5/month credit | ✅ Yes | Usually enough for small apps |
| Render | Always free | ✅ Yes | Spins down after inactivity |
| Fly.io | 3 VMs, 3GB storage | ✅ Yes | Always-on free tier |
| Google Cloud Run | 2M requests/month | ✅ Yes | Requires Google account |
| PythonAnywhere | Always free | ❌ No | Limited external requests, manual setup |

## Recommendation

**For Docker deployment (easiest)**: Start with **Railway** - it automatically detects your Dockerfile and deploys it with zero configuration.

**For always-on free Docker**: Use **Fly.io** - it has a generous always-on free tier.

**For high-traffic auto-scaling**: Use **Google Cloud Run** - generous free tier with automatic scaling.

**For non-Docker**: Use **PythonAnywhere** if you prefer traditional deployment.

## Docker vs Non-Docker

**Advantages of Docker deployment:**
- ✅ Deploy exactly as you develop (same environment)
- ✅ No need for Procfile or runtime.txt
- ✅ Consistent across all platforms
- ✅ Easy to test locally before deploying
- ✅ Your Dockerfile is already production-ready

**Your Dockerfile is production-ready:**
- Uses Gunicorn (production WSGI server)
- Handles PORT environment variable automatically
- Collects static files during build
- Optimized for production
- Includes PostgreSQL client for database operations

## Testing Docker Locally

Before deploying, test your Docker container locally:

```bash
# Build the image
docker build -t budget-app .

# Run the container
docker run -p 8000:8000 \
  -e SECRET_KEY=test-secret-key \
  -e DEBUG=True \
  -e ALLOWED_HOSTS=localhost \
  budget-app

# Or use docker-compose
docker-compose up --build
```

Your app will be available at `http://localhost:8000`
