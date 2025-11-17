AWS S3 Setup and Vercel Environment

This document explains how to provision an S3 bucket and configure the app to
upload images to S3. The app will automatically prefer S3 when the required
environment variables are present; otherwise it falls back to storing images
in the database as base64.

Required environment variables (set these in Vercel / environment or locally):

- `AWS_S3_BUCKET`: the S3 bucket name (must exist and be public-readable for the simple URL to work)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION` (optional): region like `us-east-1` or `eu-west-1`. If omitted, `us-east-1` is assumed.

How to create a bucket (AWS CLI):

1. Create the bucket:

```pwsh
aws s3api create-bucket --bucket your-bucket-name --region us-east-1
```

2. Make the bucket publicly readable (simple setup; for production prefer signed URLs or CloudFront):

```pwsh
aws s3api put-bucket-policy --bucket your-bucket-name --policy '{"Version":"2012-10-17","Statement":[{"Sid":"PublicRead","Effect":"Allow","Principal":"*","Action":["s3:GetObject"],"Resource":["arn:aws:s3:::your-bucket-name/*"]}]}'
```

Note: Public buckets expose files to anyone. For secure production setups use presigned URLs or a CDN.

Set env vars in Vercel (example):

```pwsh
vercel env add AWS_S3_BUCKET production
vercel env add AWS_ACCESS_KEY_ID production
vercel env add AWS_SECRET_ACCESS_KEY production
vercel env add AWS_REGION production
```

After setting env vars, redeploy the project. The app will then attempt to
upload images to S3 when saving settings.

Fallback behavior

- If S3 is not configured, the app stores images in the SQLite DB as base64
  in the `Settings` table. This persists as long as the database file is
  preserved. On serverless platforms where the file system is ephemeral (like
  Vercel), prefer S3 or managed storage.

Security notes

- Do NOT commit AWS credentials to source control.
- For production, prefer IAM roles, short-lived credentials or a secure
  secrets store.
