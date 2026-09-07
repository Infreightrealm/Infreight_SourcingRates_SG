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
          LOW: "text-success-foreground bg-success/10 border-success/25",
          MEDIUM: "text-warning-foreground bg-warning/10 border-warning/25",
          HIGH: "text-destructive-foreground bg-destructive/10 border-destructive/25",
        };

        return (
          <div
            key={idx}
            className={`
              bg-card/70 backdrop-blur-md
              border border-warning/25 rounded-2xl p-5 shadow-card transition-colors
              flex flex-col md:flex-row md:items-center justify-between gap-4
              animate-fade-in-down ${report.risk_level === 'HIGH' ? 'animate-shake' : ''}
            `}
            style={{ animationDelay: `${idx * 0.05}s` }}
          >
            <div className="space-y-2 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="inline-flex items-center gap-1.5 rounded-full border border-warning/25 bg-warning/12 px-2.5 py-0.5 text-xs font-semibold text-warning-foreground">
                  <span className="size-1.5 animate-ping rounded-full bg-warning" />
                  Self-Healing Alert
                </span>
                <span className="text-xs font-bold text-foreground">
                  {report.carrier} Connector
                </span>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md border ${riskColors[report.risk_level]}`}>
                  Risk: {report.risk_level}
                </span>
              </div>

              <h4 className="text-xs font-medium text-muted-foreground">
                Action failed: <strong className="text-foreground">{report.expected_action}</strong>
              </h4>

              <p className="max-w-3xl text-xs leading-relaxed text-foreground">
                <strong>Diagnosis:</strong> {report.reasoning}
              </p>

              <div className="space-y-1 font-mono text-[11px] text-muted-foreground">
                <div>Original selector: <code className="rounded border border-border bg-muted px-1 py-0.5 text-destructive-foreground">{report.original_selector}</code></div>
                <div>Proposed fix: <code className="rounded border border-border bg-muted px-1 py-0.5 text-success-foreground">{report.suggested_selector}</code></div>
              </div>
            </div>

            <div className="flex items-center gap-2.5 md:self-center">
              <button
                onClick={() => handleReject(report)}
                className="
                  btn-interactive rounded-lg border border-border bg-secondary px-4 py-2
                  text-xs font-semibold text-secondary-foreground hover:bg-accent
                "
              >
                Reject
              </button>
              <button
                onClick={() => handleApprove(report)}
                className="
                  btn-interactive shine-on-hover rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600
                  px-4 py-2 text-xs font-semibold text-white shadow-panel hover:brightness-110
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
