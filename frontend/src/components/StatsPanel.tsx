import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { getStats, getCacheStats } from '../lib/api';
import { StatsResponse, CacheStatsResponse } from '../lib/api';
import CategoryBadge from './CategoryBadge';

interface StatsPanelProps {
  className?: string;
  refreshInterval?: number;
}

export const StatsPanel: React.FC<StatsPanelProps> = ({ 
  className = '', 
  refreshInterval = 30000 
}) => {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [cacheStats, setCacheStats] = useState<CacheStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setError(null);
      const [statsData, cacheData] = await Promise.all([
        getStats(),
        getCacheStats()
      ]);
      setStats(statsData);
      setCacheStats(cacheData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchStats, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>System Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2">Loading stats...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>System Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-red-600 text-center p-4">
            <p>Error loading stats: {error}</p>
            <button 
              onClick={fetchStats}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getCacheHitRate = (level: string) => {
    if (!cacheStats?.cache_statistics?.[`${level}_cache`]) return 0;
    const cache = cacheStats.cache_statistics[`${level}_cache`];
    return cache.hit_rate || 0;
  };

  const getCacheHealth = (level: string) => {
    if (!cacheStats?.health_status?.[`${level}_cache`]) return 'unknown';
    return cacheStats.health_status[`${level}_cache`].status;
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          System Statistics
          <button 
            onClick={fetchStats}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Refresh
          </button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Document Statistics */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Documents</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {stats?.total_documents || 0}
              </div>
              <div className="text-sm text-gray-600">Total Documents</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {stats?.total_chunks || 0}
              </div>
              <div className="text-sm text-gray-600">Total Chunks</div>
            </div>
          </div>
        </div>

        {/* Category Breakdown */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Categories</h3>
          <div className="space-y-2">
            {stats?.categories && Object.entries(stats.categories).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between">
                <CategoryBadge category={category} />
                <Badge variant="secondary">{count} docs</Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Cache Statistics */}
        {cacheStats && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Cache Performance</h3>
            <div className="space-y-3">
              {['l1', 'l2', 'l3'].map(level => (
                <div key={level} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="flex items-center">
                    <span className="font-medium capitalize">{level} Cache</span>
                    <Badge 
                      variant={getCacheHealth(level) === 'healthy' ? 'default' : 'destructive'}
                      className="ml-2"
                    >
                      {getCacheHealth(level)}
                    </Badge>
                  </div>
                  <div className="text-sm text-gray-600">
                    {getCacheHitRate(level).toFixed(1)}% hit rate
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Classification Statistics */}
        {stats?.classification_stats && Object.keys(stats.classification_stats).length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Classification</h3>
            <div className="space-y-2">
              {Object.entries(stats.classification_stats).map(([category, stats]) => (
                <div key={category} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <CategoryBadge category={category} />
                  <div className="text-sm text-gray-600">
                    {stats.doc_count || 0} docs
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Last Updated */}
        <div className="text-xs text-gray-500 text-center pt-2 border-t">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </CardContent>
    </Card>
  );
};

export default StatsPanel;
