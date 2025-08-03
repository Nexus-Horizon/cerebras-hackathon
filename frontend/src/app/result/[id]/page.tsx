import { notFound } from 'next/navigation';
import ResultCard from '@/components/ResultCard';

async function fetchResult(id: string) {
  try {
    const response = await fetch(`http://localhost:8000/analyze/result/${id}`);
    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch result:', error);
    return null;
  }
}

export default async function ResultPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const resolvedParams = await params;
  const {id} = resolvedParams;

  const result = await fetchResult(id);
  
  if (!result) {
    notFound();
  }

  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6 text-center">Analysis Result</h1>
      <ResultCard
        key={result.timestamp}
        question={result.question}
        task={result.task}
        result={result.result}
        latency={result.latency}
        frontendTime={result.frontendTime || 0}
        modelName={result.modelName}
        modelLatency={result.modelLatency}
        resultId={result.id}
      />
      
    </div>
  );
}
