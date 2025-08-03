# AutoModel - AI Image Analysis Platform

This is a Next.js frontend application for AutoModel, an AI-powered image analysis platform that processes images using various machine learning models and tasks.

## Features

- **Multi-Task AI Analysis**: Supports OCR (Optical Character Recognition), Image Captioning, and VQA (Visual Question Answering)
- **Real-time Performance Metrics**: Displays backend latency and frontend processing times for each analysis
- **Model Leaderboard**: Shows real-time performance rankings of different AI models based on speed
- **Shareable Results**: Generate shareable links and QR codes for analysis results
- **Dark Mode**: Toggle between light and dark themes for better user experience
- **Responsive Design**: Works seamlessly across desktop and mobile devices

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Main upload and analysis interface
│   │   ├── layout.tsx           # Root layout with metadata
│   │   └── result/
│   │       └── [id]/
│   │           └── page.tsx    # Individual result display page
│   └── components/
│       ├── ResultCard.tsx       # Component for displaying analysis results
│       ├── LeaderboardTable.tsx # Speed leaderboard for AI models
│       ├── Logo.tsx             # Application logo component
│       └── BrowserExtensionHandler.tsx # Browser extension integration
├── public/                     # Static assets and favicon files
└── next.config.ts              # Next.js configuration
```

## Getting Started

First, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Alternative Setup (Windows)
- Double-click `start.bat` to start the development server

### Prerequisites
- Node.js 18+ installed
- Backend API server running on `http://localhost:8000`

## How It Works

1. **Upload & Question**: Users upload an image file (JPG/PNG) and ask a question about it
2. **AI Processing**: The application sends the image and question to the backend API for analysis
3. **Results Display**: Analysis results are displayed with performance metrics including:
   - Task type (OCR, Captioning, VQA)
   - Model used for processing
   - Backend processing latency
   - Frontend processing time
4. **Leaderboard**: Real-time model performance rankings are shown in a fixed panel
5. **Sharing**: Each result can be shared via generated links or QR codes

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
