"use client";

import { useState, useEffect } from "react";
import { toast } from "sonner";

interface RepairReport {
  carrier: string;
  step_name: string;
  url: string;
  original_selector: string;
  error_message: string;
  expected_action: string;
  suggested_selector: string;
  reasoning: string;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  status: string;
  dir_name: string;
}

interface SelfHealingAlertsProps {
  backendUrl: string;
  isSearching: boolean;
}

export default function SelfHealingAlerts({ backendUrl, isSearching }: SelfHealingAlertsProps) {
  const [reports, setReports] = useState<RepairReport[]>([]);

  // Fetch pending reports
  const fetchReports = async () => {
    try {
      const res = await fetch(`${backendUrl}/api/connector-repair/reports`);
      if (res.ok) {
        const data = await res.json();
        // Only show reports that are pending review
        const pending = data.filter((r: RepairReport) => r.status === "PENDING_REVIEW");
        setReports(pending);
      }
    } catch (err) {
      console.error("Failed to fetch repair reports:", err);
    }
  };

  // Poll for reports if searching is active
  useEffect(() => {
    fetchReports();
    
    const interval = setInterval(() => {
      fetchReports();
    }, 4000);

    return () => clearInterval(interval);
  }, [backendUrl, isSearching]);

  const handleApprove = async (report: RepairReport) => {
    try {
      const res = await fetch(`${backendUrl}/api/connector-repair/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          carrier: report.carrier,
          step_name: report.step_name,
          original_selector: report.original_selector,
          approved_selector: report.suggested_selector,
        }),
      });

      if (res.ok) {
        toast.success(`Approved selector fix for ${report.carrier}! Fix saved in memory.`);
        fetchReports(); // Refresh
      } else {
        toast.error("Failed to approve repair suggestion.");
      }
    } catch (err) {
      toast.error("Network error approving selector fix.");
    }
  };

  const handleReject = async (report: RepairReport) => {
    try {
      const res = await fetch(`${backendUrl}/api/connector-repair/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          carrier: report.carrier,
          step_name: report.step_name,
        }),
      });

      if (res.ok) {
        toast.info(`Rejected selector fix for ${report.carrier}.`);
        fetchReports(); // Refresh
      } else {
        toast.error("Failed to reject repair suggestion.");
      }
    } catch (err) {
      toast.error("Network error rejecting selector fix.");
    }
  };

  if (reports.length === 0) return null;

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-top-4 duration-300">
      {reports.map((report, idx) => {
        const riskColors = {
          LOW: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
          MEDIUM: "text-amber-500 bg-amber-500/10 border-amber-500/20",
          HIGH: "text-rose-500 bg-rose-500/10 border-rose-500/20",
        };

        return (
          <div
            key={idx}
            className="
              bg-white/60 dark:bg-white/[0.02] backdrop-blur-md
              border border-amber-200 dark:border-amber-500/20 rounded-2xl p-5
              shadow-lg shadow-amber-500/5 transition-colors
              flex flex-col md:flex-row md:items-center justify-between gap-4
            "
          >
            <div className="space-y-2 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 dark:bg-amber-500/15 dark:text-amber-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping" />
                  Self-Healing Alert
                </span>
                <span className="text-xs font-bold text-slate-800 dark:text-white">
                  {report.carrier} Connector
                </span>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md border ${riskColors[report.risk_level]}`}>
                  Risk: {report.risk_level}
                </span>
              </div>

              <h4 className="text-xs font-medium text-slate-600 dark:text-white/60">
                Action failed: <strong className="text-slate-900 dark:text-white">{report.expected_action}</strong>
              </h4>

              <p className="text-xs text-slate-700 dark:text-white/80 max-w-3xl leading-relaxed">
                <strong>Diagnosis:</strong> {report.reasoning}
              </p>

              <div className="text-[11px] font-mono text-slate-500 dark:text-white/40 space-y-1">
                <div>Original selector: <code className="bg-slate-200 dark:bg-white/5 px-1 py-0.5 rounded text-rose-500">{report.original_selector}</code></div>
                <div>Proposed fix: <code className="bg-slate-200 dark:bg-white/5 px-1 py-0.5 rounded text-emerald-500">{report.suggested_selector}</code></div>
              </div>
            </div>

            <div className="flex items-center gap-2.5 md:self-center">
              <button
                onClick={() => handleReject(report)}
                className="
                  px-4 py-2 rounded-xl text-xs font-semibold border border-slate-300 dark:border-white/10
                  hover:bg-slate-100 dark:hover:bg-white/5 text-slate-600 dark:text-white/70 transition-all duration-150
                "
              >
                Reject
              </button>
              <button
                onClick={() => handleApprove(report)}
                className="
                  px-4 py-2 rounded-xl text-xs font-semibold
                  bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700
                  text-white shadow-md shadow-emerald-500/10 hover:scale-102 active:scale-98 transition-all duration-150
                "
              >
                Approve & Save
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
