#!/bin/bash
cd /Users/yernuraidarbek/Desktop/FYP

# Create a temporary Swift package to generate project structure
mkdir -p TempProject
cd TempProject

# Use swift package init
swift package init --type executable --name AcousticAuthApp

echo "Temporary package created. Now opening Xcode to create proper iOS project..."
