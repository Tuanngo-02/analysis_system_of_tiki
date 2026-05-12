#!/usr/bin/env bash

# Quick Start Script for Tiki Recommendation System
# Hướng dẫn chạy nhanh cho hệ thống gợi ý sản phẩm Tiki

echo "🚀 Tiki Recommendation System - Quick Start"
echo "==========================================="
echo ""

# Check if backend is already running
echo "Kiểm tra backend..."
if lsof -Pi :8000 -sTCP:LISTEN -t > /dev/null ; then
  echo "✅ Backend đã chạy trên port 8000"
else
  echo "❌ Backend chưa chạy. Vui lòng khởi động backend trước:"
  echo ""
  echo "  cd backend"
  echo "  uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
  echo ""
fi

# Check if frontend dependencies are installed
echo ""
echo "Kiểm tra Frontend dependencies..."
if [ ! -d "frontend/node_modules" ]; then
  echo "📦 Cài đặt Node dependencies..."
  cd frontend
  npm install
  cd ..
  echo "✅ Dependencies installed"
else
  echo "✅ Dependencies đã được cài đặt"
fi

echo ""
echo "🎉 Tất cả sẵn sàng!"
echo ""
echo "Bước tiếp theo:"
echo "  1. Mở terminal mới"
echo "  2. cd frontend && npm run dev"
echo "  3. Mở http://localhost:5173 trong browser"
echo ""
