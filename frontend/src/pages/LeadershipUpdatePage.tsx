import React, { useState } from "react";
import { FileText, Loader2 } from "lucide-react";
import { LoadingState, ErrorState, EmptyState, PageHeader } from "@/components/layout";
import { fetchLeadershipUpdate } from "@/lib/api";

interface LeadershipSection {
  title: string;
  content: string;
}

export default function LeadershipUpdatePage() {
  const [sections, setSections] = useState<LeadershipSection[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchLeadershipUpdate();
      setSections(response.sections || []);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingState message="Generating leadership update..." />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={handleGenerate} />;
  }

  return (
    <section id="leadership-update" className="prose">
      <PageHeader title="Weekly Leadership Update" subtitle="Generated AI update based on active pipeline, revenue, and operations." />

      {/* Generate Update button */}
      <div className="mb-6 text-center">
        <button 
          onClick={handleGenerate}
          className="px-6 py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors flex items-center gap-2 mx-auto"
        >
          <FileText className="w-5 h-5" />
          Generate update
        </button>
      </div>

      {sections.length === 0 && (
        <EmptyState
          icon={FileText}
          title="No update generated"
          description="Click the button above to synthesize the latest business data into a leadership update."
          onAction={handleGenerate}
          actionLabel="Generate Now"
        />
      )}

      {/* Sections */}
      {sections.length > 0 && (
        <div className="space-y-6">
          {sections.map((section) => (
            <div key={section.title} className="rounded-lg border bg-card p-6 shadow-sm">
              <h3 className="text-xl font-bold mb-4">{section.title}</h3>
              <p className="whitespace-pre-wrap">{section.content}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}