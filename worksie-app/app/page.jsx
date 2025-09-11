import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold mb-8">Welcome to Worksie</h1>
      <Link href="/new-estimate" className="bg-blue-500 text-white px-6 py-3 rounded-lg text-xl">
        Create New Estimate
      </Link>
    </div>
  );
}
