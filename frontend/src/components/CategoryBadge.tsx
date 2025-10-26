import React from 'react';
import { Badge } from './ui/badge';

interface CategoryBadgeProps {
  category: string;
  confidence?: number;
  className?: string;
}

const categoryColors = {
  legal: 'bg-red-100 text-red-800 border-red-200',
  technical: 'bg-blue-100 text-blue-800 border-blue-200',
  financial: 'bg-green-100 text-green-800 border-green-200',
  hr: 'bg-purple-100 text-purple-800 border-purple-200',
  general: 'bg-gray-100 text-gray-800 border-gray-200',
};

const categoryIcons = {
  legal: '⚖️',
  technical: '🔧',
  financial: '💰',
  hr: '👥',
  general: '📄',
};

export const CategoryBadge: React.FC<CategoryBadgeProps> = ({ 
  category, 
  confidence, 
  className = '' 
}) => {
  const colorClass = categoryColors[category as keyof typeof categoryColors] || categoryColors.general;
  const icon = categoryIcons[category as keyof typeof categoryIcons] || categoryIcons.general;
  
  return (
    <Badge 
      variant="outline" 
      className={`${colorClass} ${className}`}
      title={confidence ? `Confidence: ${(confidence * 100).toFixed(1)}%` : undefined}
    >
      <span className="mr-1">{icon}</span>
      <span className="capitalize">{category}</span>
      {confidence && (
        <span className="ml-1 text-xs opacity-75">
          {(confidence * 100).toFixed(0)}%
        </span>
      )}
    </Badge>
  );
};

export default CategoryBadge;
