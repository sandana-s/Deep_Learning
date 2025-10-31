import React from 'react';

function AgentSelector({ selectedAgent, onSelectAgent }) {
  return (
    <div>
      <select
        value={selectedAgent}
        onChange={(e) => onSelectAgent(e.target.value)}
        className="w-full p-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-400"
      >
        <option value="auto">Auto — pick best agent</option>
        <option value="qa">Q&A — ask questions</option>
        <option value="summarize">Summarize — document summaries</option>
        <option value="ppt">PPT — create presentations</option>
      </select>
      <div className="mt-2 text-xs text-gray-500">Choose agent mode</div>
    </div>
  );
}

export default AgentSelector;
