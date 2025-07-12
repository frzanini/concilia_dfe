#!/bin/bash

# CONFIGURAÇÕES
REGION="sa-east-1"
REPO_NAME="concilia-dfe"
IMAGE_TAG="latest"

# OBTÉM O ACCOUNT ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}"

echo "Account ID: $ACCOUNT_ID"
echo "ECR URI: $ECR_URI"

# CRIA REPOSITÓRIO (SE NÃO EXISTIR)
aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "🔨 Repositório não existe. Criando..."
  aws ecr create-repository --repository-name $REPO_NAME --region $REGION
else
  echo "📦 Repositório já existe."
fi

# LOGIN NO ECR
echo "🔐 Autenticando no ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# BUILD DA IMAGEM
echo "🐳 Buildando imagem Docker..."
docker build -t $REPO_NAME .

# TAGUEIA A IMAGEM
echo "🏷️  Tagueando imagem..."
docker tag $REPO_NAME:latest $ECR_URI:$IMAGE_TAG

# ENVIA PARA O ECR
echo "📤 Enviando imagem para o ECR..."
docker push $ECR_URI:$IMAGE_TAG

echo "✅ Deploy da imagem para o ECR finalizado com sucesso!"
