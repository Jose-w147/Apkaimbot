#!/bin/bash
echo "========================================="
echo "Auto-Aim Detector APK Builder"
echo "========================================="
if ! command -v buildozer &> /dev/null
then
echo "Instalando Buildozer..."
pip install buildozer
fi
echo "Instalando dependências..."
pip install -r requirements.txt
echo "Limpando builds anteriores..."
rm -rf .buildozer
rm -rf build
rm -rf bin
echo "Construindo APK..."
buildozer android debug
if [ $? -eq 0 ]; then
echo "========================================="
echo "APK criado com sucesso!"
echo "Localização: bin/*.apk"
echo "========================================="
else
echo "Erro ao construir APK"
exit 1
fi