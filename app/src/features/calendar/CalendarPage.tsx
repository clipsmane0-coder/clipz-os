"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon, Clock, GripVertical, Trash2, Video } from "lucide-react";
import { useScheduleList } from "../../lib/api/hooks";
import type { FScheduleView } from "../../lib/api/mapper";

const platformColors: Record<string, string> = {
  TikTok: "bg-rose-500",
  Instagram: "bg-pink-500",
  "YouTube Shorts": "bg-red-500",
  Threads: "bg-zinc-400",
  X: "bg-cyan-500",
};

function formatMonthYear(date: Date) {
  return date.toLocaleDateString("en-US", { month: "long", year: "numeric" });
}

function getDaysInMonth(date: Date) {
  const year = date.getFullYear();
  const month = date.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const days: (number | null)[] = [];
  for (let i = 0; i < firstDay; i++) days.push(null);
  for (let i = 1; i <= daysInMonth; i++) days.push(i);
  return days;
}

export function CalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]);
  const [view, setView] = useState<"month" | "week" | "day">("week");

  const { data: schedData, isLoading } = useScheduleList({ pageSize: 100 });
  const scheduledPosts = schedData?.data || [];

  const postsByDate: Record<string, FScheduleView[]> = {};
  scheduledPosts.forEach((post) => {
    if (!postsByDate[post.scheduledDate]) postsByDate[post.scheduledDate] = [];
    postsByDate[post.scheduledDate].push(post);
  });

  const today = new Date().toISOString().split("T")[0];
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  if (isLoading) {
    return (
      <div className="p-4 lg:p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-64 bg-clipz-surface rounded" />
          <div className="grid grid-cols-7 gap-2">
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="h-[400px] bg-clipz-panel rounded-xl border border-clipz-border" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const getWeekDays = (baseDate: Date) => {
    const start = new Date(baseDate);
    start.setDate(start.getDate() - start.getDay());
    return Array.from({ length: 7 }, (_, i) => {
      const d = new Date(start);
      d.setDate(d.getDate() + i);
      return d;
    });
  };

  const weekDays = getWeekDays(currentMonth);
  const monthDays = getDaysInMonth(currentMonth);

  const prevMonth = () => {
    const d = new Date(currentMonth);
    d.setMonth(d.getMonth() - 1);
    setCurrentMonth(d);
  };

  const nextMonth = () => {
    const d = new Date(currentMonth);
    d.setMonth(d.getMonth() + 1);
    setCurrentMonth(d);
  };

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Posting Calendar</h2>
          <p className="text-[12px] text-clipz-text-muted">
            {scheduledPosts.length} posts scheduled across {Object.keys(postsByDate).length} days
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-clipz-border overflow-hidden">
            {(["day", "week", "month"] as const).map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`px-3 py-1.5 text-[11px] font-medium capitalize transition-colors ${
                  view === v ? "bg-clipz-accent text-white" : "text-clipz-text-muted hover:text-white"
                }`}
              >
                {v}
              </button>
            ))}
          </div>
          <button className="flex items-center gap-2 rounded-lg bg-clipz-accent px-3.5 py-2 text-[12px] font-medium text-white hover:bg-clipz-accent/90">
            <Plus size={14} /> Schedule Post
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button onClick={prevMonth} className="p-1.5 rounded-md text-clipz-text-muted hover:text-white hover:bg-clipz-surface">
            <ChevronLeft size={16} />
          </button>
          <h3 className="text-[15px] font-semibold text-white min-w-[180px]">{formatMonthYear(currentMonth)}</h3>
          <button onClick={nextMonth} className="p-1.5 rounded-md text-clipz-text-muted hover:text-white hover:bg-clipz-surface">
            <ChevronRight size={16} />
          </button>
          <button className="ml-2 px-2.5 py-1 rounded-md border border-clipz-border bg-clipz-surface text-[11px] text-clipz-text-muted hover:text-white">
            Today
          </button>
        </div>
        <div className="flex items-center gap-3">
          {Object.entries(platformColors).slice(0, 5).map(([platform, color]) => (
            <div key={platform} className="flex items-center gap-1.5 text-[11px] text-clipz-text-muted">
              <div className={`h-2 w-2 rounded-full ${color}`} /> {platform}
            </div>
          ))}
        </div>
      </div>

      {view === "week" && (
        <div className="grid grid-cols-7 gap-2">
          {weekDays.map((day) => {
            const dateStr = day.toISOString().split("T")[0];
            const posts = postsByDate[dateStr] || [];
            const isToday = dateStr === today;
            const isSelected = dateStr === selectedDate;

            return (
              <div
                key={dateStr}
                onClick={() => setSelectedDate(dateStr)}
                className={`rounded-xl border bg-clipz-panel overflow-hidden min-h-[400px] transition-all cursor-pointer ${
                  isSelected ? "border-clipz-accent shadow-lg shadow-violet-500/5" : "border-clipz-border hover:border-clipz-border/80"
                }`}
              >
                <div className={`px-3 py-2 border-b border-clipz-border-soft ${isToday ? "bg-clipz-accent/10" : ""}`}>
                  <div className="text-[10px] text-clipz-text-dim uppercase">{dayNames[day.getDay()]}</div>
                  <div className="flex items-baseline justify-between">
                    <span className={`text-[18px] font-bold ${isToday ? "text-clipz-accent-soft" : "text-white"}`}>
                      {day.getDate()}
                    </span>
                    {posts.length > 0 && <span className="text-[10px] text-clipz-text-dim">{posts.length}</span>}
                  </div>
                </div>
                <div className="p-2 space-y-1.5">
                  {posts.slice(0, 4).map((post) => (
                    <div key={post.id} className="group relative rounded-lg bg-clipz-surface border border-clipz-border-soft overflow-hidden hover:border-clipz-accent/30">
                      <div className="flex gap-2 p-2">
                        <div className="relative h-10 w-8 shrink-0 rounded overflow-hidden bg-clipz-elevated">
                          <img src={post.thumbnail} alt="" className="h-full w-full object-cover" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] text-white font-medium truncate">{post.clipTitle}</p>
                          <div className="flex items-center gap-1 mt-0.5">
                            <div className={`h-1.5 w-1.5 rounded-full ${platformColors[post.platform] || "bg-zinc-500"}`} />
                            <span className="text-[9px] text-clipz-text-dim">{post.scheduledTime}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {posts.length > 4 && <div className="text-[10px] text-clipz-text-dim text-center py-1">+{posts.length - 4} more</div>}
                  {posts.length === 0 && <div className="h-16 flex items-center justify-center"><Plus size={14} className="text-clipz-text-dim opacity-30" /></div>}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {view === "month" && (
        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="grid grid-cols-7 border-b border-clipz-border">
            {dayNames.map((day) => (
              <div key={day} className="py-2 text-center text-[11px] text-clipz-text-muted font-medium">{day}</div>
            ))}
          </div>
          <div className="grid grid-cols-7">
            {monthDays.map((day, i) => {
              if (day === null) return <div key={i} className="h-24 border-b border-r border-clipz-border-soft bg-clipz-bg/30" />;
              const dateStr = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day).toISOString().split("T")[0];
              const posts = postsByDate[dateStr] || [];
              const isToday = dateStr === today;
              return (
                <div
                  key={i}
                  onClick={() => setSelectedDate(dateStr)}
                  className={`h-24 border-b border-r border-clipz-border-soft p-1.5 cursor-pointer hover:bg-clipz-surface/30 ${isToday ? "bg-clipz-accent/5" : ""}`}
                >
                  <div className={`text-[11px] mb-1 ${isToday ? "text-clipz-accent-soft font-bold" : "text-clipz-text-muted"}`}>{day}</div>
                  <div className="space-y-1">
                    {posts.slice(0, 2).map((post) => (
                      <div key={post.id} className="flex items-center gap-1.5 rounded bg-clipz-surface border border-clipz-border-soft px-1.5 py-0.5">
                        <div className={`h-1.5 w-1.5 rounded-full ${platformColors[post.platform] || "bg-zinc-500"}`} />
                        <span className="text-[9px] text-white truncate flex-1">{post.clipTitle}</span>
                      </div>
                    ))}
                    {posts.length > 2 && <div className="text-[9px] text-clipz-text-dim pl-3">+{posts.length - 2} more</div>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {view === "day" && (
        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="p-4 border-b border-clipz-border-soft">
            <h4 className="text-[14px] font-semibold text-white">
              {new Date(selectedDate).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
            </h4>
            <p className="text-[11px] text-clipz-text-muted">
              {(postsByDate[selectedDate] || []).length} posts scheduled
            </p>
          </div>
          <div className="p-4 space-y-3">
            {(postsByDate[selectedDate] || []).map((post) => (
              <div key={post.id} className="flex items-center gap-3 rounded-lg border border-clipz-border bg-clipz-surface p-3 hover:border-clipz-accent/30 group">
                <div className="text-clipz-text-dim cursor-grab"><GripVertical size={14} /></div>
                <div className="relative h-14 w-24 shrink-0 rounded overflow-hidden bg-clipz-elevated">
                  <img src={post.thumbnail} alt="" className="h-full w-full object-cover" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] font-medium text-white truncate">{post.clipTitle}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className={`h-1.5 w-1.5 rounded-full ${platformColors[post.platform] || "bg-zinc-500"}`} />
                    <span className="text-[11px] text-clipz-text-muted">{post.platform}</span>
                    <span className="text-[11px] text-clipz-text-dim">·</span>
                    <span className="text-[11px] text-clipz-text-muted">{post.scheduledTime}</span>
                  </div>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100">
                  <button className="p-1.5 text-clipz-text-muted hover:text-white rounded hover:bg-clipz-elevated"><Video size={13} /></button>
                  <button className="p-1.5 text-rose-400 hover:text-rose-300 rounded hover:bg-rose-500/10"><Trash2 size={13} /></button>
                </div>
              </div>
            ))}
            {(postsByDate[selectedDate] || []).length === 0 && (
              <div className="text-center py-12 text-clipz-text-dim">
                <CalendarIcon size={32} className="mx-auto mb-2 opacity-30" />
                <p className="text-[12px]">No posts scheduled for this day</p>
                <button className="mt-3 px-3 py-1.5 rounded-md bg-clipz-accent/15 text-clipz-accent-soft text-[11px] font-medium">Add post</button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
