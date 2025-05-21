
import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// Mock citation data over time
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

interface CitationChartProps {
  baseCitations: number;
}

const CitationChart = ({ baseCitations }: CitationChartProps) => {
  const [data, setData] = useState<any[]>([]);
  const [activeView, setActiveView] = useState<'yearly' | 'cumulative'>('yearly');
  
  useEffect(() => {
    setData(generateMockCitationData(baseCitations));
  }, [baseCitations]);

  return (
    <Card className="col-span-3">
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Citation Trends</CardTitle>
            <CardDescription>
              How your research is being cited over time
            </CardDescription>
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
      </CardHeader>
      <CardContent className="h-80">
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
            />
            <Tooltip />
            {activeView === 'yearly' ? (
              <Line
                type="monotone"
                dataKey="citations"
                stroke="#A6CE39"
                strokeWidth={2}
                activeDot={{ r: 6 }}
                name="Citations"
              />
            ) : (
              <Line
                type="monotone"
                dataKey="cumulativeCitations"
                stroke="#A6CE39"
                strokeWidth={2}
                activeDot={{ r: 6 }}
                name="Total Citations"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default CitationChart;
