#!/bin/bash
echo "Starting Worksie deploy sequence..."
npm install
npm run build
firebase deploy --only hosting
echo "Deployment complete!"
