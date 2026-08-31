import React from 'react';
import { Entities } from '../types';
import { Users, Calendar, DollarSign, MapPin, Tag } from 'lucide-react';

interface EntityPillsProps {
  entities: Entities;
}

export const EntityPills: React.FC<EntityPillsProps> = ({ entities }) => {
  const hasParties = entities.parties && entities.parties.length > 0;
  const hasDates = entities.dates && entities.dates.length > 0;
  const hasAmounts = entities.amounts && entities.amounts.length > 0;
  const hasLocations = entities.locations && entities.locations.length > 0;

  const totalEntities =
    (entities.parties?.length || 0) +
    (entities.dates?.length || 0) +
    (entities.amounts?.length || 0) +
    (entities.locations?.length || 0);

  if (totalEntities === 0) return null;

  return (
    <div className="glass-panel p-6 rounded-2xl border border-surface-border space-y-4">
      <div className="flex items-center justify-between border-b border-surface-border pb-3">
        <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Tag className="w-4 h-4 text-secondary-500" />
          Extracted Contract Metadata
        </h4>
        <span className="text-xs text-gray-400 font-mono">{totalEntities} Entities Identified</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Parties */}
        {hasParties && (
          <div className="space-y-2 p-3.5 rounded-xl bg-surface-subtle border border-surface-border">
            <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-400 uppercase tracking-wide">
              <Users className="w-3.5 h-3.5" />
              <span>Parties Involved ({entities.parties.length})</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {entities.parties.map((party, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-md bg-indigo-500/10 border border-indigo-500/30 text-indigo-200 text-xs font-medium"
                >
                  {party}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Dates */}
        {hasDates && (
          <div className="space-y-2 p-3.5 rounded-xl bg-surface-subtle border border-surface-border">
            <div className="flex items-center gap-1.5 text-xs font-bold text-cyan-400 uppercase tracking-wide">
              <Calendar className="w-3.5 h-3.5" />
              <span>Key Dates ({entities.dates.length})</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {entities.dates.map((date, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-200 text-xs font-medium font-mono"
                >
                  {date}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Amounts */}
        {hasAmounts && (
          <div className="space-y-2 p-3.5 rounded-xl bg-surface-subtle border border-surface-border">
            <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400 uppercase tracking-wide">
              <DollarSign className="w-3.5 h-3.5" />
              <span>Financial Values ({entities.amounts.length})</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {entities.amounts.map((amount, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-200 text-xs font-medium font-mono"
                >
                  {amount}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Locations */}
        {hasLocations && (
          <div className="space-y-2 p-3.5 rounded-xl bg-surface-subtle border border-surface-border">
            <div className="flex items-center gap-1.5 text-xs font-bold text-purple-400 uppercase tracking-wide">
              <MapPin className="w-3.5 h-3.5" />
              <span>Jurisdiction / Locations ({entities.locations.length})</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {entities.locations.map((loc, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-md bg-purple-500/10 border border-purple-500/30 text-purple-200 text-xs font-medium"
                >
                  {loc}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
