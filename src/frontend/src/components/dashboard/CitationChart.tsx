import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface CitationData {
  year: number;
  citations: number;
  cumulativeCitations: number;
}

interface CitationChartProps {
  citationData?: CitationData[];
  isLoading?: boolean;
  error?: string;
}

const CitationChart = ({ citationData, isLoading = false, error }: CitationChartProps) => {
  const [activeView, setActiveView] = useState<'yearly' | 'cumulative'>('yearly');
  
  // Show loading state
  if (isLoading) {
    return (
      <Card className="col-span-3">
        <CardHeader>
          <CardTitle>Citation Trends</CardTitle>
          <CardDescription>Loading citation data...</CardDescription>
        </CardHeader>
        <CardContent className="h-80 flex items-center justify-center">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orcid-green"></div>
            <span className="text-gray-600">Analyzing citations...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show error state
  if (error) {
    return (
      <Card className="col-span-3">
        <CardHeader>
          <CardTitle>Citation Trends</CardTitle>
          <CardDescription>Error loading citation data</CardDescription>
        </CardHeader>
        <CardContent className="h-80 flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 mb-2">⚠️ Unable to load citation data</div>
            <div className="text-sm text-gray-600">{error}</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const totalCitations = citationData && citationData.length > 0 ? citationData[citationData.length - 1]?.cumulativeCitations || 0 : 0;
  const hasData = citationData && citationData.length > 0;

  return (
    <Card className="col-span-3">
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Citation Trends</CardTitle>
            <CardDescription>
              {hasData ? "How your research is being cited over time • Real data from ORCID & CrossRef" : "Citation trends will appear when data is loaded"}
            </CardDescription>
          </div>
          <div className="flex items-center space-x-3">
            {hasData && (
              <div className="text-sm text-gray-600">
                Total: <span className="font-semibold text-orcid-green">{totalCitations}</span>
              </div>
            )}
            <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg text-sm">
              <button
                onClick={() => setActiveView('yearly')}
                className={`px-3 py-1 rounded ${
                  activeView === 'yearly' 
                    ? 'bg-white shadow-sm' 
                    : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                Yearly
              </button>
              <button
                onClick={() => setActiveView('cumulative')}
                className={`px-3 py-1 rounded ${
                  activeView === 'cumulative' 
                    ? 'bg-white shadow-sm' 
                    : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                Cumulative
              </button>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={hasData ? citationData : []}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="year" 
              tick={{ fontSize: 12 }}
              tickMargin={10}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickMargin={10}
              domain={[0, 'dataMax']}
            />
            <Tooltip 
              labelFormatter={(year) => `Year: ${year}`}
              formatter={(value, name) => [value, name]}
            />
            {hasData && (
              activeView === 'yearly' ? (
                <Line
                  type="monotone"
                  dataKey="citations"
                  stroke="#A6CE39"
                  strokeWidth={2}
                  activeDot={{ r: 6 }}
                  name="Citations"
                  connectNulls={false}
                />
              ) : (
                <Line
                  type="monotone"
                  dataKey="cumulativeCitations"
                  stroke="#A6CE39"
                  strokeWidth={2}
                  activeDot={{ r: 6 }}
                  name="Total Citations"
                  connectNulls={false}
                />
              )
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default CitationChart;
