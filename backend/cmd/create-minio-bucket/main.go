// create-minio-bucket creates the S3_BUCKET on the S3-compatible endpoint (e.g. MinIO).
// Loads S3_* from env (and .env). Run from backend dir: go run ./cmd/create-minio-bucket
package main

import (
	"bytes"
	"context"
	"errors"
	"log"
	"os"
	"os/exec"
)

func main() {
	myCtx := context.Background()
	config, err := loadConfig()
	if err != nil {
		log.Fatal(err)
	}
	if err := ensureAWSCLI(); err != nil {
		log.Fatal(err)
	}
	env := buildAWSEnv(config)
	if err := ensureBucket(myCtx, config, env); err != nil {
		log.Fatal(err)
	}
}

type bucketConfig struct {
	accessKey string
	bucket    string
	endpoint  string
	region    string
	secretKey string
}

func loadConfig() (bucketConfig, error) {
	config := bucketConfig{
		endpoint:  os.Getenv("S3_ENDPOINT"),
		accessKey: os.Getenv("S3_ACCESS_KEY_ID"),
		secretKey: os.Getenv("S3_SECRET_ACCESS_KEY"),
		bucket:    os.Getenv("S3_BUCKET"),
		region:    os.Getenv("S3_REGION"),
	}
	if config.region == "" {
		config.region = "us-east-1"
	}
	if config.endpoint == "" || config.accessKey == "" || config.secretKey == "" || config.bucket == "" {
		return bucketConfig{}, errors.New("set S3_ENDPOINT, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_BUCKET in .env")
	}
	return config, nil
}

func ensureAWSCLI() error {
	if _, err := exec.LookPath("aws"); err != nil {
		return errors.New("aws CLI not found in PATH")
	}
	return nil
}

func buildAWSEnv(config bucketConfig) []string {
	return append(os.Environ(),
		"AWS_ACCESS_KEY_ID="+config.accessKey,
		"AWS_SECRET_ACCESS_KEY="+config.secretKey,
		"AWS_REGION="+config.region,
		"AWS_DEFAULT_REGION="+config.region,
	)
}

func ensureBucket(ctx context.Context, config bucketConfig, env []string) error {
	endpointArgs := buildEndpointArgs(config.endpoint)
	headArgs := buildHeadArgs(endpointArgs, config.bucket)
	if err := runAWS(ctx, env, headArgs); err == nil {
		log.Printf("Bucket %q already exists.", config.bucket)
		return nil
	}

	createArgs := buildCreateArgs(endpointArgs, config)
	if err := runAWS(ctx, env, createArgs); err != nil {
		return errors.New("CreateBucket failed")
	}
	log.Printf("Bucket %q created.", config.bucket)
	return nil
}

func buildEndpointArgs(endpoint string) []string {
	if endpoint == "" {
		return []string{}
	}
	return []string{"--endpoint-url", endpoint}
}

func buildHeadArgs(endpointArgs []string, bucket string) []string {
	args := append([]string{}, endpointArgs...)
	return append(args, "s3api", "head-bucket", "--bucket", bucket)
}

func buildCreateArgs(endpointArgs []string, config bucketConfig) []string {
	args := []string{"s3api", "create-bucket", "--bucket", config.bucket}
	if config.region != "" && config.region != "us-east-1" {
		args = append(
			args,
			"--create-bucket-configuration",
			"LocationConstraint="+config.region,
		)
	}
	return append(endpointArgs, args...)
}

func runAWS(ctx context.Context, env []string, args []string) error {
	cmd := exec.CommandContext(ctx, "aws", args...)
	cmd.Env = env

	var stderr bytes.Buffer
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		if stderr.Len() > 0 {
			return errors.New(stderr.String())
		}
		return err
	}
	return nil
}
