import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// Mock citation data over time (fallback)
const generateMockCitationData = (baseValue: number) => {
  const data = [];
  const currentYear = new Date().getFullYear();
  let cumulativeCitations = 0;

  // Generate 5 years of data, with a slight randomization
  for (let i = 0; i < 5; i++) {
    const year = currentYear - 4 + i;
    const yearCitations = Math.round(baseValue * (1 + i * 0.4) * (0.8 + Math.random() * 0.4));
    cumulativeCitations += yearCitations;
    
    data.push({
      year,
      citations: yearCitations,
      cumulativeCitations
    });
  }

  return data;
};

interface CitationData {
  year: number;
  citations: number;
  cumulativeCitations: number;
}

interface CitationChartProps {
  citationData?: CitationData[];
  baseCitations?: number;
  isLoading?: boolean;
  error?: string;
}

const CitationChart = ({ citationData, baseCitations = 10, isLoading = false, error }: CitationChartProps) => {
  const [data, setData] = useState<CitationData[]>([]);
  const [activeView, setActiveView] = useState<'yearly' | 'cumulative'>('yearly');
  
  useEffect(() => {
    if (citationData && citationData.length > 0) {
      // Use real citation data
      setData(citationData);
    } else if (!isLoading && !error) {
      // Fallback to mock data if no real data and not loading
      setData(generateMockCitationData(baseCitations));
    }
  }, [citationData, baseCitations, isLoading, error]);

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

  const totalCitations = data.length > 0 ? data[data.length - 1]?.cumulativeCitations || 0 : 0;
  const dataSource = citationData && citationData.length > 0 ? "Real data from ORCID & CrossRef" : "Sample data";

  return (
    <Card className="col-span-3">
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Citation Trends</CardTitle>
            <CardDescription>
              How your research is being cited over time • {dataSource}
            </CardDescription>
          </div>
          <div className="flex items-center space-x-3">
            <div className="text-sm text-gray-600">
              Total: <span className="font-semibold text-orcid-green">{totalCitations}</span>
            </div>
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
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
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
              {activeView === 'yearly' ? (
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
              )}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <div className="text-lg mb-2">📊</div>
              <div>No citation data available</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CitationChart;
