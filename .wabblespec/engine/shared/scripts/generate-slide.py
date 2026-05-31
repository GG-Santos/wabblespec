#!/usr/bin/env python3
"""
generate-slide.py — HTML slide generator with embedded design token system.

Produces a self-contained HTML presentation using Chart.js (CDN) and
CSS custom properties sourced from the ui-ux-pro-max color palette database.
All visual values use var(--token) references — no raw hex/rgb in property values.

Usage:
    python generate-slide.py --query "Analytics Dashboard" --output slide.html
    python generate-slide.py --query "SaaS" --chart-type bar --title "Q1 Results" --output out.html
    python generate-slide.py --query "Fintech" --chart-type pie --data "40,35,25" --labels "A,B,C" --output slide.html

Arguments:
    --query      Product type query (matched against 161 embedded palettes)
    --output     Output HTML file path (default: slide.html)
    --chart-type Chart type: line|bar|pie|doughnut|scatter|area (default: bar)
    --title      Slide title (default: derived from query)
    --subtitle   Slide subtitle (optional)
    --data       Comma-separated data values for chart (default: demo data)
    --labels     Comma-separated labels for chart data points
    --list       Output list of all available palette names and exit

Exit codes:
    0   Success
    1   Argument error
"""

import argparse
import sys
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# EMBEDDED DESIGN TOKEN DATA
# Source: ui-ux-pro-max-skill-main/src/ui-ux-pro-max/data/colors.csv
# Each entry: (primary, on_primary, secondary, on_secondary, accent, on_accent,
#              background, foreground, card, card_fg, muted, muted_fg,
#              border, destructive, on_destructive, ring)
# ---------------------------------------------------------------------------

PALETTES = {
    "SaaS (General)":                  ("#2563EB","#FFFFFF","#3B82F6","#FFFFFF","#EA580C","#FFFFFF","#F8FAFC","#1E293B","#FFFFFF","#1E293B","#E9EFF8","#64748B","#E2E8F0","#DC2626","#FFFFFF","#2563EB"),
    "Micro SaaS":                      ("#6366F1","#FFFFFF","#818CF8","#0F172A","#059669","#FFFFFF","#F5F3FF","#1E1B4B","#FFFFFF","#1E1B4B","#EBEFF9","#64748B","#E0E7FF","#DC2626","#FFFFFF","#6366F1"),
    "E-commerce":                      ("#059669","#FFFFFF","#10B981","#0F172A","#EA580C","#FFFFFF","#ECFDF5","#064E3B","#FFFFFF","#064E3B","#E8F1F3","#64748B","#A7F3D0","#DC2626","#FFFFFF","#059669"),
    "E-commerce Luxury":               ("#1C1917","#FFFFFF","#44403C","#FFFFFF","#A16207","#FFFFFF","#FAFAF9","#0C0A09","#FFFFFF","#0C0A09","#E8ECF0","#64748B","#D6D3D1","#DC2626","#FFFFFF","#1C1917"),
    "B2B Service":                     ("#0F172A","#FFFFFF","#334155","#FFFFFF","#0369A1","#FFFFFF","#F8FAFC","#020617","#FFFFFF","#020617","#E8ECF1","#64748B","#E2E8F0","#DC2626","#FFFFFF","#0F172A"),
    "Financial Dashboard":             ("#0F172A","#FFFFFF","#1E293B","#FFFFFF","#22C55E","#0F172A","#020617","#F8FAFC","#0E1223","#F8FAFC","#1A1E2F","#94A3B8","#334155","#EF4444","#FFFFFF","#0F172A"),
    "Analytics Dashboard":             ("#1E40AF","#FFFFFF","#3B82F6","#FFFFFF","#D97706","#FFFFFF","#F8FAFC","#1E3A8A","#FFFFFF","#1E3A8A","#E9EEF6","#64748B","#DBEAFE","#DC2626","#FFFFFF","#1E40AF"),
    "Healthcare App":                  ("#0891B2","#FFFFFF","#22D3EE","#0F172A","#059669","#FFFFFF","#ECFEFF","#164E63","#FFFFFF","#164E63","#E8F1F6","#64748B","#A5F3FC","#DC2626","#FFFFFF","#0891B2"),
    "Educational App":                 ("#4F46E5","#FFFFFF","#818CF8","#0F172A","#EA580C","#FFFFFF","#EEF2FF","#1E1B4B","#FFFFFF","#1E1B4B","#EBEEF8","#64748B","#C7D2FE","#DC2626","#FFFFFF","#4F46E5"),
    "Creative Agency":                 ("#EC4899","#FFFFFF","#F472B6","#0F172A","#0891B2","#FFFFFF","#FDF2F8","#831843","#FFFFFF","#831843","#F1EEF5","#64748B","#FBCFE8","#DC2626","#FFFFFF","#EC4899"),
    "Portfolio/Personal":              ("#18181B","#FFFFFF","#3F3F46","#FFFFFF","#2563EB","#FFFFFF","#FAFAFA","#09090B","#FFFFFF","#09090B","#E8ECF0","#64748B","#E4E4E7","#DC2626","#FFFFFF","#18181B"),
    "Gaming":                          ("#7C3AED","#FFFFFF","#A78BFA","#0F172A","#F43F5E","#FFFFFF","#0F0F23","#E2E8F0","#1E1C35","#E2E8F0","#27273B","#94A3B8","#4C1D95","#EF4444","#FFFFFF","#7C3AED"),
    "Government/Public Service":       ("#0F172A","#FFFFFF","#334155","#FFFFFF","#0369A1","#FFFFFF","#F8FAFC","#020617","#FFFFFF","#020617","#E8ECF1","#64748B","#E2E8F0","#DC2626","#FFFFFF","#0F172A"),
    "Fintech/Crypto":                  ("#F59E0B","#0F172A","#FBBF24","#0F172A","#8B5CF6","#FFFFFF","#0F172A","#F8FAFC","#222735","#F8FAFC","#272F42","#94A3B8","#334155","#EF4444","#FFFFFF","#F59E0B"),
    "Social Media App":                ("#E11D48","#FFFFFF","#FB7185","#0F172A","#2563EB","#FFFFFF","#FFF1F2","#881337","#FFFFFF","#881337","#F0ECF2","#64748B","#FECDD3","#DC2626","#FFFFFF","#E11D48"),
    "Productivity Tool":               ("#0D9488","#FFFFFF","#14B8A6","#0F172A","#EA580C","#FFFFFF","#F0FDFA","#134E4A","#FFFFFF","#134E4A","#E8F1F4","#64748B","#99F6E4","#DC2626","#FFFFFF","#0D9488"),
    "Design System/Component Library": ("#4F46E5","#FFFFFF","#6366F1","#FFFFFF","#EA580C","#FFFFFF","#EEF2FF","#312E81","#FFFFFF","#312E81","#EBEEF8","#64748B","#C7D2FE","#DC2626","#FFFFFF","#4F46E5"),
    "AI/Chatbot Platform":             ("#7C3AED","#FFFFFF","#A78BFA","#0F172A","#0891B2","#FFFFFF","#FAF5FF","#1E1B4B","#FFFFFF","#1E1B4B","#ECEEF9","#64748B","#DDD6FE","#DC2626","#FFFFFF","#7C3AED"),
    "NFT/Web3 Platform":               ("#8B5CF6","#FFFFFF","#A78BFA","#0F172A","#FBBF24","#0F172A","#0F0F23","#F8FAFC","#1E1D35","#F8FAFC","#27273B","#94A3B8","#4C1D95","#EF4444","#FFFFFF","#8B5CF6"),
    "Creator Economy Platform":        ("#EC4899","#FFFFFF","#F472B6","#0F172A","#EA580C","#FFFFFF","#FDF2F8","#831843","#FFFFFF","#831843","#F1EEF5","#64748B","#FBCFE8","#DC2626","#FFFFFF","#EC4899"),
    "Remote Work/Collaboration Tool":  ("#6366F1","#FFFFFF","#818CF8","#0F172A","#059669","#FFFFFF","#F5F3FF","#312E81","#FFFFFF","#312E81","#EBEFF9","#64748B","#E0E7FF","#DC2626","#FFFFFF","#6366F1"),
    "Mental Health App":               ("#8B5CF6","#FFFFFF","#C4B5FD","#0F172A","#059669","#FFFFFF","#FAF5FF","#4C1D95","#FFFFFF","#4C1D95","#EDEFF9","#64748B","#EDE9FE","#DC2626","#FFFFFF","#8B5CF6"),
    "Pet Tech App":                    ("#F97316","#0F172A","#FB923C","#0F172A","#2563EB","#FFFFFF","#FFF7ED","#9A3412","#FFFFFF","#9A3412","#F1F0F0","#64748B","#FED7AA","#DC2626","#FFFFFF","#F97316"),
    "Smart Home/IoT Dashboard":        ("#1E293B","#FFFFFF","#334155","#FFFFFF","#22C55E","#0F172A","#0F172A","#F8FAFC","#1B2336","#F8FAFC","#272F42","#94A3B8","#475569","#EF4444","#FFFFFF","#1E293B"),
    "EV/Charging Ecosystem":           ("#0891B2","#FFFFFF","#22D3EE","#0F172A","#16A34A","#FFFFFF","#ECFEFF","#164E63","#FFFFFF","#164E63","#E8F1F6","#64748B","#A5F3FC","#DC2626","#FFFFFF","#0891B2"),
    "Subscription Box Service":        ("#D946EF","#FFFFFF","#E879F9","#0F172A","#EA580C","#FFFFFF","#FDF4FF","#86198F","#FFFFFF","#86198F","#F0EEF9","#64748B","#F5D0FE","#DC2626","#FFFFFF","#D946EF"),
    "Podcast Platform":                ("#1E1B4B","#FFFFFF","#312E81","#FFFFFF","#F97316","#0F172A","#0F0F23","#F8FAFC","#1B1B30","#F8FAFC","#27273B","#94A3B8","#4338CA","#EF4444","#FFFFFF","#1E1B4B"),
    "Dating App":                      ("#E11D48","#FFFFFF","#FB7185","#0F172A","#EA580C","#FFFFFF","#FFF1F2","#881337","#FFFFFF","#881337","#F0ECF2","#64748B","#FECDD3","#DC2626","#FFFFFF","#E11D48"),
    "Micro-Credentials/Badges Platform":("#0369A1","#FFFFFF","#0EA5E9","#0F172A","#A16207","#FFFFFF","#F0F9FF","#0C4A6E","#FFFFFF","#0C4A6E","#E7EFF5","#64748B","#BAE6FD","#DC2626","#FFFFFF","#0369A1"),
    "Knowledge Base/Documentation":    ("#475569","#FFFFFF","#64748B","#FFFFFF","#2563EB","#FFFFFF","#F8FAFC","#1E293B","#FFFFFF","#1E293B","#EAEFF3","#64748B","#E2E8F0","#DC2626","#FFFFFF","#475569"),
    "Hyperlocal Services":             ("#059669","#FFFFFF","#10B981","#0F172A","#EA580C","#FFFFFF","#ECFDF5","#064E3B","#FFFFFF","#064E3B","#E8F1F3","#64748B","#A7F3D0","#DC2626","#FFFFFF","#059669"),
    "Beauty/Spa/Wellness Service":     ("#EC4899","#FFFFFF","#F9A8D4","#0F172A","#8B5CF6","#FFFFFF","#FDF2F8","#831843","#FFFFFF","#831843","#F1EEF5","#64748B","#FBCFE8","#DC2626","#FFFFFF","#EC4899"),
    "Luxury/Premium Brand":            ("#1C1917","#FFFFFF","#44403C","#FFFFFF","#A16207","#FFFFFF","#FAFAF9","#0C0A09","#FFFFFF","#0C0A09","#E8ECF0","#64748B","#D6D3D1","#DC2626","#FFFFFF","#1C1917"),
    "Restaurant/Food Service":         ("#DC2626","#FFFFFF","#F87171","#0F172A","#A16207","#FFFFFF","#FEF2F2","#450A0A","#FFFFFF","#450A0A","#F0EDF1","#64748B","#FECACA","#DC2626","#FFFFFF","#DC2626"),
    "Fitness/Gym App":                 ("#F97316","#0F172A","#FB923C","#0F172A","#22C55E","#0F172A","#1F2937","#F8FAFC","#313742","#F8FAFC","#37414F","#94A3B8","#374151","#EF4444","#FFFFFF","#F97316"),
    "Real Estate/Property":            ("#0F766E","#FFFFFF","#14B8A6","#0F172A","#0369A1","#FFFFFF","#F0FDFA","#134E4A","#FFFFFF","#134E4A","#E8F0F3","#64748B","#99F6E4","#DC2626","#FFFFFF","#0F766E"),
    "Travel/Tourism Agency":           ("#0EA5E9","#0F172A","#38BDF8","#0F172A","#EA580C","#FFFFFF","#F0F9FF","#0C4A6E","#FFFFFF","#0C4A6E","#E8F2F8","#64748B","#BAE6FD","#DC2626","#FFFFFF","#0EA5E9"),
    "Hotel/Hospitality":               ("#1E3A8A","#FFFFFF","#3B82F6","#FFFFFF","#A16207","#FFFFFF","#F8FAFC","#1E40AF","#FFFFFF","#1E40AF","#E9EEF5","#64748B","#BFDBFE","#DC2626","#FFFFFF","#1E3A8A"),
    "Wedding/Event Planning":          ("#DB2777","#FFFFFF","#F472B6","#0F172A","#A16207","#FFFFFF","#FDF2F8","#831843","#FFFFFF","#831843","#F0EDF4","#64748B","#FBCFE8","#DC2626","#FFFFFF","#DB2777"),
    "Legal Services":                  ("#1E3A8A","#FFFFFF","#1E40AF","#FFFFFF","#B45309","#FFFFFF","#F8FAFC","#0F172A","#FFFFFF","#0F172A","#E9EEF5","#64748B","#CBD5E1","#DC2626","#FFFFFF","#1E3A8A"),
    "Insurance Platform":              ("#0369A1","#FFFFFF","#0EA5E9","#0F172A","#16A34A","#FFFFFF","#F0F9FF","#0C4A6E","#FFFFFF","#0C4A6E","#E7EFF5","#64748B","#BAE6FD","#DC2626","#FFFFFF","#0369A1"),
    "Banking/Traditional Finance":     ("#0F172A","#FFFFFF","#1E3A8A","#FFFFFF","#A16207","#FFFFFF","#F8FAFC","#020617","#FFFFFF","#020617","#E8ECF1","#64748B","#E2E8F0","#DC2626","#FFFFFF","#0F172A"),
    "Online Course/E-learning":        ("#0D9488","#FFFFFF","#2DD4BF","#0F172A","#EA580C","#FFFFFF","#F0FDFA","#134E4A","#FFFFFF","#134E4A","#E8F1F4","#64748B","#5EEAD4","#DC2626","#FFFFFF","#0D9488"),
    "Non-profit/Charity":              ("#0891B2","#FFFFFF","#22D3EE","#0F172A","#EA580C","#FFFFFF","#ECFEFF","#164E63","#FFFFFF","#164E63","#E8F1F6","#64748B","#A5F3FC","#DC2626","#FFFFFF","#0891B2"),
    "Music Streaming":                 ("#1E1B4B","#FFFFFF","#4338CA","#FFFFFF","#22C55E","#0F172A","#0F0F23","#F8FAFC","#1B1B30","#F8FAFC","#27273B","#94A3B8","#312E81","#EF4444","#FFFFFF","#1E1B4B"),
    "Video Streaming/OTT":             ("#0F0F23","#FFFFFF","#1E1B4B","#FFFFFF","#E11D48","#FFFFFF","#000000","#F8FAFC","#0C0C0D","#F8FAFC","#181818","#94A3B8","#312E81","#EF4444","#FFFFFF","#0F0F23"),
    "Job Board/Recruitment":           ("#0369A1","#FFFFFF","#0EA5E9","#0F172A","#16A34A","#FFFFFF","#F0F9FF","#0C4A6E","#FFFFFF","#0C4A6E","#E7EFF5","#64748B","#BAE6FD","#DC2626","#FFFFFF","#0369A1"),
    "Marketplace (P2P)":               ("#7C3AED","#FFFFFF","#A78BFA","#0F172A","#16A34A","#FFFFFF","#FAF5FF","#4C1D95","#FFFFFF","#4C1D95","#ECEEF9","#64748B","#DDD6FE","#DC2626","#FFFFFF","#7C3AED"),
    "Logistics/Delivery":              ("#2563EB","#FFFFFF","#3B82F6","#FFFFFF","#EA580C","#FFFFFF","#EFF6FF","#1E40AF","#FFFFFF","#1E40AF","#E9EFF8","#64748B","#BFDBFE","#DC2626","#FFFFFF","#2563EB"),
    "Agriculture/Farm Tech":           ("#15803D","#FFFFFF","#22C55E","#0F172A","#A16207","#FFFFFF","#F0FDF4","#14532D","#FFFFFF","#14532D","#E8F0F1","#64748B","#BBF7D0","#DC2626","#FFFFFF","#15803D"),
    "Construction/Architecture":       ("#64748B","#FFFFFF","#94A3B8","#0F172A","#EA580C","#FFFFFF","#F8FAFC","#334155","#FFFFFF","#334155","#EBF0F5","#64748B","#E2E8F0","#DC2626","#FFFFFF","#64748B"),
    "Automotive/Car Dealership":       ("#1E293B","#FFFFFF","#334155","#FFFFFF","#DC2626","#FFFFFF","#F8FAFC","#0F172A","#FFFFFF","#0F172A","#E9EDF1","#64748B","#E2E8F0","#DC2626","#FFFFFF","#1E293B"),
    "Photography Studio":              ("#18181B","#FFFFFF","#27272A","#FFFFFF","#F8FAFC","#0F172A","#000000","#FAFAFA","#0C0C0C","#FAFAFA","#181818","#94A3B8","#3F3F46","#EF4444","#FFFFFF","#18181B"),
    "Coworking Space":                 ("#F59E0B","#0F172A","#FBBF24","#0F172A","#2563EB","#FFFFFF","#FFFBEB","#78350F","#FFFFFF","#78350F","#F1F2EF","#64748B","#FDE68A","#DC2626","#FFFFFF","#F59E0B"),
    "Home Services (Plumber/Electrician)": ("#1E40AF","#FFFFFF","#3B82F6","#FFFFFF","#EA580C","#FFFFFF","#EFF6FF","#1E3A8A","#FFFFFF","#1E3A8A","#E9EEF6","#64748B","#BFDBFE","#DC2626","#FFFFFF","#1E40AF"),
    "Childcare/Daycare":               ("#F472B6","#0F172A","#FBCFE8","#0F172A","#16A34A","#FFFFFF","#FDF2F8","#9D174D","#FFFFFF","#9D174D","#F1F0F6","#64748B","#FCE7F3","#DC2626","#FFFFFF","#F472B6"),
    "Senior Care/Elderly":             ("#0369A1","#FFFFFF","#38BDF8","#0F172A","#16A34A","#FFFFFF","#F0F9FF","#0C4A6E","#FFFFFF","#0C4A6E","#E7EFF5","#64748B","#E0F2FE","#DC2626","#FFFFFF","#0369A1"),
    "Medical Clinic":                  ("#0891B2","#FFFFFF","#22D3EE","#0F172A","#16A34A","#FFFFFF","#F0FDFA","#134E4A","#FFFFFF","#134E4A","#E8F1F6","#64748B","#CCFBF1","#DC2626","#FFFFFF","#0891B2"),
    "Pharmacy/Drug Store":             ("#15803D","#FFFFFF","#22C55E","#0F172A","#0369A1","#FFFFFF","#F0FDF4","#14532D","#FFFFFF","#14532D","#E8F0F1","#64748B","#BBF7D0","#DC2626","#FFFFFF","#15803D"),
    "Dental Practice":                 ("#0EA5E9","#0F172A","#38BDF8","#0F172A","#0EA5E9","#0F172A","#F0F9FF","#0C4A6E","#FFFFFF","#0C4A6E","#E8F2F8","#64748B","#BAE6FD","#DC2626","#FFFFFF","#0EA5E9"),
    "Veterinary Clinic":               ("#0D9488","#FFFFFF","#14B8A6","#0F172A","#EA580C","#FFFFFF","#F0FDFA","#134E4A","#FFFFFF","#134E4A","#E8F1F4","#64748B","#99F6E4","#DC2626","#FFFFFF","#0D9488"),
    "Florist/Plant Shop":              ("#15803D","#FFFFFF","#22C55E","#0F172A","#EC4899","#FFFFFF","#F0FDF4","#14532D","#FFFFFF","#14532D","#E8F0F1","#64748B","#BBF7D0","#DC2626","#FFFFFF","#15803D"),
    "Bakery/Cafe":                     ("#92400E","#FFFFFF","#B45309","#FFFFFF","#92400E","#FFFFFF","#FEF3C7","#78350F","#FFFFFF","#78350F","#EDEEF0","#64748B","#FDE68A","#DC2626","#FFFFFF","#92400E"),
    "Brewery/Winery":                  ("#7C2D12","#FFFFFF","#B91C1C","#FFFFFF","#A16207","#FFFFFF","#FEF2F2","#450A0A","#FFFFFF","#450A0A","#ECEDF0","#64748B","#FECACA","#DC2626","#FFFFFF","#7C2D12"),
    "Airline":                         ("#1E3A8A","#FFFFFF","#3B82F6","#FFFFFF","#EA580C","#FFFFFF","#EFF6FF","#1E40AF","#FFFFFF","#1E40AF","#E9EEF5","#64748B","#BFDBFE","#DC2626","#FFFFFF","#1E3A8A"),
    "News/Media Platform":             ("#DC2626","#FFFFFF","#EF4444","#FFFFFF","#1E40AF","#FFFFFF","#FEF2F2","#450A0A","#FFFFFF","#450A0A","#F0EDF1","#64748B","#FECACA","#DC2626","#FFFFFF","#DC2626"),
    "Magazine/Blog":                   ("#18181B","#FFFFFF","#3F3F46","#FFFFFF","#EC4899","#FFFFFF","#FAFAFA","#09090B","#FFFFFF","#09090B","#E8ECF0","#64748B","#E4E4E7","#DC2626","#FFFFFF","#18181B"),
    "Freelancer Platform":             ("#6366F1","#FFFFFF","#818CF8","#0F172A","#16A34A","#FFFFFF","#EEF2FF","#312E81","#FFFFFF","#312E81","#EBEFF9","#64748B","#C7D2FE","#DC2626","#FFFFFF","#6366F1"),
    "Marketing Agency":                ("#EC4899","#FFFFFF","#F472B6","#0F172A","#0891B2","#FFFFFF","#FDF2F8","#831843","#FFFFFF","#831843","#F1EEF5","#64748B","#FBCFE8","#DC2626","#FFFFFF","#EC4899"),
    "Event Management":                ("#7C3AED","#FFFFFF","#A78BFA","#0F172A","#EA580C","#FFFFFF","#FAF5FF","#4C1D95","#FFFFFF","#4C1D95","#ECEEF9","#64748B","#DDD6FE","#DC2626","#FFFFFF","#7C3AED"),
    "Membership/Community":            ("#7C3AED","#FFFFFF","#A78BFA","#0F172A","#16A34A","#FFFFFF","#FAF5FF","#4C1D95","#FFFFFF","#4C1D95","#ECEEF9","#64748B","#DDD6FE","#DC2626","#FFFFFF","#7C3AED"),
    "Newsletter Platform":             ("#0369A1","#FFFFFF","#0EA5E9","#0F172A","#EA580C","#FFFFFF","#F0F9FF","#0C4A6E","#FFFFFF","#0C4A6E","#E7EFF5","#64748B","#BAE6FD","#DC2626","#FFFFFF","#0369A1"),
    "Digital Products/Downloads":      ("#6366F1","#FFFFFF","#818CF8","#0F172A","#16A34A","#FFFFFF","#EEF2FF","#312E81","#FFFFFF","#312E81","#EBEFF9","#64748B","#C7D2FE","#DC2626","#FFFFFF","#6366F1"),
    "Church/Religious Organization":   ("#7C3AED","#FFFFFF","#A78BFA","#0F172A","#A16207","#FFFFFF","#FAF5FF","#4C1D95","#FFFFFF","#4C1D95","#ECEEF9","#64748B","#DDD6FE","#DC2626","#FFFFFF","#7C3AED"),
    "Sports Team/Club":                ("#DC2626","#FFFFFF","#EF4444","#FFFFFF","#DC2626","#FFFFFF","#FEF2F2","#7F1D1D","#FFFFFF","#7F1D1D","#F0EDF1","#64748B","#FECACA","#DC2626","#FFFFFF","#DC2626"),
    "Museum/Gallery":                  ("#18181B","#FFFFFF","#27272A","#FFFFFF","#18181B","#FFFFFF","#FAFAFA","#09090B","#FFFFFF","#09090B","#E8ECF0","#64748B","#E4E4E7","#DC2626","#FFFFFF","#18181B"),
    "Theater/Cinema":                  ("#1E1B4B","#FFFFFF","#312E81","#FFFFFF","#CA8A04","#0F172A","#0F0F23","#F8FAFC","#1B1B30","#F8FAFC","#27273B","#94A3B8","#4338CA","#EF4444","#FFFFFF","#1E1B4B"),
    "Language Learning App":           ("#4F46E5","#FFFFFF","#818CF8","#0F172A","#16A34A","#FFFFFF","#EEF2FF","#312E81","#FFFFFF","#312E81","#EBEEF8","#64748B","#C7D2FE","#DC2626","#FFFFFF","#4F46E5"),
    "Coding Bootcamp":                 ("#0F172A","#FFFFFF","#1E293B","#FFFFFF","#22C55E","#0F172A","#020617","#F8FAFC","#0E1223","#F8FAFC","#1A1E2F","#94A3B8","#334155","#EF4444","#FFFFFF","#0F172A"),
    "Cybersecurity Platform":          ("#00FF41","#0F172A","#0D0D0D","#FFFFFF","#FF3333","#FFFFFF","#000000","#E0E0E0","#0C130E","#E0E0E0","#181818","#94A3B8","#1F1F1F","#EF4444","#FFFFFF","#00FF41"),
    "Developer Tool / IDE":            ("#1E293B","#FFFFFF","#334155","#FFFFFF","#22C55E","#0F172A","#0F172A","#F8FAFC","#1B2336","#F8FAFC","#272F42","#94A3B8","#475569","#EF4444","#FFFFFF","#1E293B"),
    "Biotech / Life Sciences":         ("#0EA5E9","#0F172A","#0284C7","#FFFFFF","#059669","#FFFFFF","#F0F9FF","#0C4A6E","#FFFFFF","#0C4A6E","#E8F2F8","#64748B","#BAE6FD","#DC2626","#FFFFFF","#0EA5E9"),
    "Space Tech / Aerospace":          ("#F8FAFC","#0F172A","#94A3B8","#0F172A","#3B82F6","#FFFFFF","#0B0B10","#F8FAFC","#1E1E23","#F8FAFC","#232328","#94A3B8","#1E293B","#EF4444","#FFFFFF","#F8FAFC"),
    "Architecture / Interior":         ("#171717","#FFFFFF","#404040","#FFFFFF","#A16207","#FFFFFF","#FFFFFF","#171717","#FFFFFF","#171717","#E8ECF0","#64748B","#E5E5E5","#DC2626","#FFFFFF","#171717"),
    "Quantum Computing Interface":     ("#00FFFF","#0F172A","#7B61FF","#FFFFFF","#FF00FF","#FFFFFF","#050510","#E0E0FF","#101823","#E0E0FF","#1D1D28","#94A3B8","#333344","#EF4444","#FFFFFF","#00FFFF"),
    "Biohacking / Longevity App":      ("#FF4D4D","#FFFFFF","#4D94FF","#FFFFFF","#059669","#FFFFFF","#F5F5F7","#1C1C1E","#FFFFFF","#1C1C1E","#F2EEF2","#64748B","#E5E5EA","#DC2626","#FFFFFF","#FF4D4D"),
    "Autonomous Drone Fleet Manager":  ("#00FF41","#0F172A","#008F11","#FFFFFF","#FF3333","#FFFFFF","#0D1117","#E6EDF3","#182424","#E6EDF3","#25292F","#94A3B8","#30363D","#EF4444","#FFFFFF","#00FF41"),
    "Generative Art Platform":         ("#18181B","#FFFFFF","#3F3F46","#FFFFFF","#EC4899","#FFFFFF","#FAFAFA","#09090B","#FFFFFF","#09090B","#E8ECF0","#64748B","#E4E4E7","#DC2626","#FFFFFF","#18181B"),
    "Spatial Computing OS / App":      ("#FFFFFF","#0F172A","#E5E5E5","#0F172A","#FFFFFF","#0F172A","#888888","#000000","#999999","#000000","#777777","#D4D4D4","#CCCCCC","#FF3B30","#FFFFFF","#007AFF"),
    "Sustainable Energy / Climate Tech":("#059669","#FFFFFF","#10B981","#0F172A","#059669","#FFFFFF","#ECFDF5","#064E3B","#FFFFFF","#064E3B","#E8F1F3","#64748B","#A7F3D0","#DC2626","#FFFFFF","#059669"),
    "Todo & Task Manager":             ("#2563EB","#FFFFFF","#3B82F6","#FFFFFF","#059669","#FFFFFF","#F8FAFC","#0F172A","#FFFFFF","#0F172A","#F1F5FD","#64748B","#E4ECFC","#DC2626","#FFFFFF","#2563EB"),
    "Personal Finance Tracker":        ("#1E40AF","#FFFFFF","#3B82F6","#FFFFFF","#059669","#FFFFFF","#0F172A","#FFFFFF","#192134","#FFFFFF","#101A34","#94A3B8","rgba(255,255,255,0.08)","#DC2626","#FFFFFF","#1E40AF"),
    "Chat & Messaging App":            ("#2563EB","#FFFFFF","#6366F1","#FFFFFF","#059669","#FFFFFF","#FFFFFF","#0F172A","#FFFFFF","#0F172A","#F1F5FD","#64748B","#E4ECFC","#DC2626","#FFFFFF","#2563EB"),
    "Notes & Writing App":             ("#78716C","#FFFFFF","#A8A29E","#FFFFFF","#D97706","#FFFFFF","#FFFBEB","#0F172A","#FFFFFF","#0F172A","#F6F6F6","#64748B","#EEEDED","#DC2626","#FFFFFF","#78716C"),
    "Habit Tracker":                   ("#D97706","#FFFFFF","#F59E0B","#0F172A","#059669","#FFFFFF","#FFFBEB","#0F172A","#FFFFFF","#0F172A","#FCF6F0","#64748B","#FAEEE1","#DC2626","#FFFFFF","#D97706"),
    "Food Delivery / On-Demand":       ("#EA580C","#FFFFFF","#F97316","#FFFFFF","#2563EB","#FFFFFF","#FFF7ED","#0F172A","#FFFFFF","#0F172A","#FDF4F0","#64748B","#FCEAE1","#DC2626","#FFFFFF","#EA580C"),
    "Ride Hailing / Transportation":   ("#1E293B","#FFFFFF","#334155","#FFFFFF","#2563EB","#FFFFFF","#0F172A","#FFFFFF","#192134","#FFFFFF","#10182B","#94A3B8","rgba(255,255,255,0.08)","#DC2626","#FFFFFF","#1E293B"),
    "Recipe & Cooking App":            ("#9A3412","#FFFFFF","#C2410C","#FFFFFF","#059669","#FFFFFF","#FFFBEB","#0F172A","#FFFFFF","#0F172A","#F8F2F0","#64748B","#F2E6E2","#DC2626","#FFFFFF","#9A3412"),
    "Meditation & Mindfulness":        ("#7C3AED","#FFFFFF","#8B5CF6","#FFFFFF","#059669","#FFFFFF","#FAF5FF","#0F172A","#FFFFFF","#0F172A","#F7F3FD","#64748B","#EFE7FC","#DC2626","#FFFFFF","#7C3AED"),
    "Weather App":                     ("#0284C7","#FFFFFF","#0EA5E9","#FFFFFF","#F59E0B","#0F172A","#F0F9FF","#0F172A","#FFFFFF","#0F172A","#EFF7FB","#64748B","#E0F0F8","#DC2626","#FFFFFF","#0284C7"),
    "CRM & Client Management":         ("#2563EB","#FFFFFF","#3B82F6","#FFFFFF","#059669","#FFFFFF","#F8FAFC","#0F172A","#FFFFFF","#0F172A","#F1F5FD","#64748B","#E4ECFC","#DC2626","#FFFFFF","#2563EB"),
    "Inventory & Stock Management":    ("#334155","#FFFFFF","#475569","#FFFFFF","#059669","#FFFFFF","#F8FAFC","#0F172A","#FFFFFF","#0F172A","#F2F3F4","#64748B","#E6E8EA","#DC2626","#FFFFFF","#334155"),
    "Booking & Appointment App":       ("#0284C7","#FFFFFF","#0EA5E9","#FFFFFF","#059669","#FFFFFF","#F0F9FF","#0F172A","#FFFFFF","#0F172A","#EFF7FB","#64748B","#E0F0F8","#DC2626","#FFFFFF","#0284C7"),
    "Invoice & Billing Tool":          ("#1E3A5F","#FFFFFF","#2563EB","#FFFFFF","#059669","#FFFFFF","#F8FAFC","#0F172A","#FFFFFF","#0F172A","#F1F3F5","#64748B","#E4E7EB","#DC2626","#FFFFFF","#1E3A5F"),
    "Grocery & Shopping List":         ("#059669","#FFFFFF","#10B981","#FFFFFF","#D97706","#FFFFFF","#ECFDF5","#0F172A","#FFFFFF","#0F172A","#F0F8F6","#64748B","#E1F2ED","#DC2626","#FFFFFF","#059669"),
    "Timer & Pomodoro":                ("#DC2626","#FFFFFF","#EF4444","#FFFFFF","#059669","#FFFFFF","#0F172A","#FFFFFF","#192134","#FFFFFF","#1F1829","#94A3B8","rgba(255,255,255,0.08)","#DC2626","#FFFFFF","#DC2626"),
    "Parenting & Baby Tracker":        ("#EC4899","#FFFFFF","#F472B6","#FFFFFF","#0284C7","#FFFFFF","#FDF2F8","#0F172A","#FFFFFF","#0F172A","#FDF4F8","#64748B","#FCE9F2","#DC2626","#FFFFFF","#EC4899"),
    "Scanner & Document Manager":      ("#1E293B","#FFFFFF","#334155","#FFFFFF","#2563EB","#FFFFFF","#F8FAFC","#0F172A","#FFFFFF","#0F172A","#F1F2F3","#64748B","#E4E5E7","#DC2626","#FFFFFF","#1E293B"),
    "Calendar & Scheduling App":       ("#2563EB","#FFFFFF","#3B82F6","#FFFFFF","#059669","#FFFFFF","#F8FAFC","#0F172A","#FFFFFF","#0F172A","#F1F5FD","#64748B","#E4ECFC","#DC2626","#FFFFFF","#2563EB"),
    "Password Manager":                ("#1E3A5F","#FFFFFF","#334155","#FFFFFF","#059669","#FFFFFF","#0F172A","#FFFFFF","#192134","#FFFFFF","#10192E","#94A3B8","rgba(255,255,255,0.08)","#DC2626","#FFFFFF","#1E3A5F"),
    "Running & Cycling GPS":           ("#EA580C","#FFFFFF","#F97316","#FFFFFF","#059669","#FFFFFF","#0F172A","#FFFFFF","#192134","#FFFFFF","#201C27","#94A3B8","rgba(255,255,255,0.08)","#DC2626","#FFFFFF","#EA580C"),
    "Sleep Tracker":                   ("#4338CA","#FFFFFF","#6366F1","#FFFFFF","#7C3AED","#FFFFFF","#0F172A","#FFFFFF","#192134","#FFFFFF","#131936","#94A3B8","rgba(255,255,255,0.08)","#DC2626","#FFFFFF","#4338CA"),
    "Calorie & Nutrition Counter":     ("#059669","#FFFFFF","#10B981","#FFFFFF","#EA580C","#FFFFFF","#ECFDF5","#0F172A","#FFFFFF","#0F172A","#F0F8F6","#64748B","#E1F2ED","#DC2626","#FFFFFF","#059669"),
    "Casual Puzzle Game":              ("#EC4899","#FFFFFF","#8B5CF6","#FFFFFF","#F59E0B","#0F172A","#FDF2F8","#0F172A","#FFFFFF","#0F172A","#FDF4F8","#64748B","#FCE9F2","#DC2626","#FFFFFF","#EC4899"),
    "Trivia & Quiz Game":              ("#2563EB","#FFFFFF","#7C3AED","#FFFFFF","#F59E0B","#0F172A","#EFF6FF","#0F172A","#FFFFFF","#0F172A","#F1F5FD","#64748B","#E4ECFC","#DC2626","#FFFFFF","#2563EB"),
    "Photo Editor & Filters":          ("#7C3AED","#FFFFFF","#6366F1","#FFFFFF","#0891B2","#FFFFFF","#0F172A","#FFFFFF","#192134","#FFFFFF","#171939","#94A3B8","rgba(255,255,255,0.08)","#DC2626","#FFFFFF","#7C3AED"),
    "Drawing & Sketching Canvas":      ("#7C3AED","#FFFFFF","#8B5CF6","#FFFFFF","#0891B2","#FFFFFF","#1C1917","#FFFFFF","#262321","#FFFFFF","#231B28","#94A3B8","rgba(255,255,255,0.08)","#DC2626","#FFFFFF","#7C3AED"),
    "VPN & Privacy Tool":              ("#1E3A5F","#FFFFFF","#334155","#FFFFFF","#22C55E","#0F172A","#0F172A","#FFFFFF","#192134","#FFFFFF","#10192E","#94A3B8","rgba(255,255,255,0.08)","#DC2626","#FFFFFF","#1E3A5F"),
    "Emergency SOS & Safety":          ("#DC2626","#FFFFFF","#EF4444","#FFFFFF","#2563EB","#FFFFFF","#FFF1F2","#0F172A","#FFFFFF","#0F172A","#FCF1F1","#64748B","#FAE4E4","#DC2626","#FFFFFF","#DC2626"),
    "Public Transit Guide":            ("#2563EB","#FFFFFF","#0891B2","#FFFFFF","#EA580C","#FFFFFF","#F8FAFC","#0F172A","#FFFFFF","#0F172A","#F1F5FD","#64748B","#E4ECFC","#DC2626","#FFFFFF","#2563EB"),
    "Local Events & Discovery":        ("#EA580C","#FFFFFF","#F97316","#FFFFFF","#2563EB","#FFFFFF","#FFF7ED","#0F172A","#FFFFFF","#0F172A","#FDF4F0","#64748B","#FCEAE1","#DC2626","#FFFFFF","#EA580C"),
    "Coding Challenge & Practice":     ("#22C55E","#0F172A","#059669","#FFFFFF","#D97706","#FFFFFF","#0F172A","#FFFFFF","#192134","#FFFFFF","#10242E","#94A3B8","rgba(255,255,255,0.08)","#DC2626","#FFFFFF","#22C55E"),
    "Home Decoration & Interior Design":("#78716C","#FFFFFF","#A8A29E","#FFFFFF","#D97706","#FFFFFF","#FAF5F2","#0F172A","#FFFFFF","#0F172A","#F6F6F6","#64748B","#EEEDED","#DC2626","#FFFFFF","#78716C"),
}

# ---------------------------------------------------------------------------
# EMBEDDED SPACING AND SHADOW TOKENS
# Source: ui-ux-pro-max design_system.py MASTER.md generation
# ---------------------------------------------------------------------------

SPACING_TOKENS = {
    "--space-xs":  "4px",
    "--space-sm":  "8px",
    "--space-md":  "16px",
    "--space-lg":  "24px",
    "--space-xl":  "32px",
    "--space-2xl": "48px",
    "--space-3xl": "64px",
}

SHADOW_TOKENS = {
    "--shadow-sm": "0 1px 2px rgba(0,0,0,0.05)",
    "--shadow-md": "0 4px 6px rgba(0,0,0,0.1)",
    "--shadow-lg": "0 10px 15px rgba(0,0,0,0.1)",
    "--shadow-xl": "0 20px 25px rgba(0,0,0,0.15)",
}

# ---------------------------------------------------------------------------
# CHART TYPE MAPPINGS
# Source: ui-ux-pro-max charts.csv
# ---------------------------------------------------------------------------

CHART_TYPES = {
    "line":     {"type": "line",      "fill": False, "label": "Trend"},
    "bar":      {"type": "bar",       "fill": False, "label": "Compare"},
    "pie":      {"type": "pie",       "fill": True,  "label": "Proportion"},
    "doughnut": {"type": "doughnut",  "fill": True,  "label": "Proportion"},
    "scatter":  {"type": "scatter",   "fill": False, "label": "Correlation"},
    "area":     {"type": "line",      "fill": True,  "label": "Area Trend"},
}

FALLBACK_PALETTE = "SaaS (General)"
CHARTJS_CDN = "https://cdn.jsdelivr.net/npm/chart.js"

# ---------------------------------------------------------------------------
# PALETTE LOOKUP
# ---------------------------------------------------------------------------

def _lookup_palette(query: str):
    """
    Find the best matching palette for a query string.
    Priority: exact match > case-insensitive > word overlap > fallback.
    Returns (palette_name, tokens_tuple).
    """
    q = query.strip()

    # 1. Exact match
    if q in PALETTES:
        return q, PALETTES[q]

    # 2. Case-insensitive match
    q_lower = q.lower()
    for name, tokens in PALETTES.items():
        if name.lower() == q_lower:
            return name, tokens

    # 3. Partial / word-overlap match
    q_words = set(re.sub(r'[^a-z0-9 ]', ' ', q_lower).split())
    best_name, best_score = None, 0
    for name, tokens in PALETTES.items():
        name_lower = name.lower()
        # Score: words in query that appear in the palette name
        name_words = set(re.sub(r'[^a-z0-9 ]', ' ', name_lower).split())
        overlap = len(q_words & name_words)
        # Bonus if query is a substring of name
        if q_lower in name_lower:
            overlap += 5
        if overlap > best_score:
            best_score = overlap
            best_name = name

    if best_name and best_score > 0:
        return best_name, PALETTES[best_name]

    # 4. Fallback
    return FALLBACK_PALETTE, PALETTES[FALLBACK_PALETTE]


def _palette_to_tokens(tokens):
    """Map the 16-tuple to named CSS custom property dict."""
    keys = [
        "--color-primary", "--color-on-primary",
        "--color-secondary", "--color-on-secondary",
        "--color-accent", "--color-on-accent",
        "--color-background", "--color-foreground",
        "--color-card", "--color-card-foreground",
        "--color-muted", "--color-muted-foreground",
        "--color-border",
        "--color-destructive", "--color-on-destructive",
        "--color-ring",
    ]
    return dict(zip(keys, tokens))

# ---------------------------------------------------------------------------
# DEMO DATA
# ---------------------------------------------------------------------------

DEMO_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
DEMO_DATA   = [42, 68, 55, 81, 73, 90]

def _parse_data(data_str):
    try:
        return [float(x.strip()) for x in data_str.split(",") if x.strip()]
    except ValueError:
        return DEMO_DATA

def _parse_labels(labels_str, data_len):
    if not labels_str:
        return [f"Item {i+1}" for i in range(data_len)]
    labels = [x.strip() for x in labels_str.split(",") if x.strip()]
    # Pad or trim to match data length
    while len(labels) < data_len:
        labels.append(f"Item {len(labels)+1}")
    return labels[:data_len]

# ---------------------------------------------------------------------------
# HTML GENERATION
# ---------------------------------------------------------------------------

def _build_chart_js_config(chart_type_key, labels, data, color_tokens):
    """Build the Chart.js dataset configuration JSON string."""
    ct = CHART_TYPES.get(chart_type_key, CHART_TYPES["bar"])
    fill = "true" if ct["fill"] else "false"

    labels_js = "[" + ", ".join(f'"{l}"' for l in labels) + "]"
    data_js   = "[" + ", ".join(str(d) for d in data) + "]"

    if chart_type_key in ("pie", "doughnut"):
        # Multi-color backgrounds for pie/doughnut
        bg_colors_js = "[" + ", ".join(
            f"'var(--color-{'primary' if i == 0 else 'secondary' if i == 1 else 'accent'})'".replace(
                "'var(--color-accent)'", "'var(--color-accent)'"
            ) for i in range(len(data))
        ) + "]"
        dataset = f"""{{
            data: {data_js},
            backgroundColor: {bg_colors_js},
            borderWidth: 2,
            borderColor: 'var(--color-card)'
        }}"""
    elif chart_type_key == "scatter":
        scatter_data = "[" + ", ".join(f"{{x: {i+1}, y: {d}}}" for i, d in enumerate(data)) + "]"
        dataset = f"""{{
            label: '{ct['label']}',
            data: {scatter_data},
            backgroundColor: 'var(--color-primary)',
            borderColor: 'var(--color-primary)',
            pointRadius: 6,
            pointHoverRadius: 8
        }}"""
    else:
        dataset = f"""{{
            label: '{ct['label']}',
            data: {data_js},
            backgroundColor: 'var(--color-primary)',
            borderColor: 'var(--color-secondary)',
            borderWidth: 2,
            fill: {fill},
            tension: 0.4,
            pointBackgroundColor: 'var(--color-accent)',
            pointRadius: 4,
            pointHoverRadius: 6
        }}"""

    options_scales = ""
    if chart_type_key not in ("pie", "doughnut"):
        options_scales = """
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: 'var(--color-border)' },
                ticks: { color: 'var(--color-muted-foreground)' }
            },
            x: {
                grid: { color: 'var(--color-border)' },
                ticks: { color: 'var(--color-muted-foreground)' }
            }
        },"""

    chart_type_js = ct["type"]

    return f"""{{
    type: '{chart_type_js}',
    data: {{
        labels: {labels_js},
        datasets: [{dataset}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            legend: {{
                labels: {{ color: 'var(--color-foreground)' }}
            }},
            tooltip: {{
                backgroundColor: 'var(--color-card)',
                titleColor: 'var(--color-foreground)',
                bodyColor: 'var(--color-muted-foreground)',
                borderColor: 'var(--color-border)',
                borderWidth: 1
            }}
        }},{options_scales}
    }}
}}"""


def generate_html(query, chart_type_key, title, subtitle, data, labels):
    """Generate the complete self-contained HTML slide."""
    palette_name, palette_tuple = _lookup_palette(query)
    color_tokens = _palette_to_tokens(palette_tuple)

    # Build :root CSS custom properties — token DEFINITIONS (exempt from validator)
    token_lines = []
    for name, value in color_tokens.items():
        token_lines.append(f"    {name}: {value};")
    for name, value in SPACING_TOKENS.items():
        token_lines.append(f"    {name}: {value};")
    for name, value in SHADOW_TOKENS.items():
        token_lines.append(f"    {name}: {value};")
    root_tokens = "\n".join(token_lines)

    chart_config = _build_chart_js_config(chart_type_key, labels, data, color_tokens)
    slide_title = title or palette_name
    subtitle_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{slide_title}</title>
<script src="{CHARTJS_CDN}"></script>
<style>
/* === DESIGN TOKEN DEFINITIONS === */
:root {{
{root_tokens}
}}

/* === LAYOUT === */
*, *::before, *::after {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    font-family: system-ui, -apple-system, sans-serif;
    background: var(--color-background);
    color: var(--color-foreground);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-xl);
}}

.slide {{
    width: 100%;
    max-width: 960px;
    background: var(--color-card);
    border-radius: 16px;
    padding: var(--space-2xl);
    box-shadow: var(--shadow-xl);
    border: 1px solid var(--color-border);
}}

/* === HEADER === */
.slide-header {{
    margin-bottom: var(--space-xl);
    padding-bottom: var(--space-lg);
    border-bottom: 2px solid var(--color-border);
}}

.palette-badge {{
    display: inline-block;
    background: var(--color-primary);
    color: var(--color-on-primary);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: var(--space-xs) var(--space-sm);
    border-radius: 4px;
    margin-bottom: var(--space-sm);
}}

.slide-title {{
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-foreground);
    line-height: 1.2;
    margin-bottom: var(--space-xs);
}}

.subtitle {{
    font-size: 1rem;
    color: var(--color-muted-foreground);
    margin-top: var(--space-xs);
}}

/* === CHART AREA === */
.chart-container {{
    position: relative;
    height: 380px;
    width: 100%;
    background: var(--color-background);
    border-radius: 12px;
    padding: var(--space-lg);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
}}

/* === FOOTER === */
.slide-footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: var(--space-xl);
    padding-top: var(--space-md);
    border-top: 1px solid var(--color-border);
    font-size: 12px;
    color: var(--color-muted-foreground);
}}

.footer-accent {{
    color: var(--color-accent);
    font-weight: 600;
}}
</style>
</head>
<body>
<div class="slide">
    <div class="slide-header">
        <span class="palette-badge">{palette_name}</span>
        <h1 class="slide-title">{slide_title}</h1>
        {subtitle_html}
    </div>
    <div class="chart-container">
        <canvas id="mainChart"></canvas>
    </div>
    <div class="slide-footer">
        <span>Generated with WabbleSpec generate-slide.py</span>
        <span class="footer-accent">Chart.js &middot; Design Tokens</span>
    </div>
</div>
<script>
const ctx = document.getElementById('mainChart').getContext('2d');
const chart = new Chart(ctx, {chart_config});
</script>
</body>
</html>
"""
    return html

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a token-safe Chart.js HTML slide.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--query", default="SaaS (General)",
                        help="Product type query for palette lookup (default: 'SaaS (General)')")
    parser.add_argument("--output", default="slide.html",
                        help="Output file path (default: slide.html)")
    parser.add_argument("--chart-type", default="bar",
                        choices=list(CHART_TYPES.keys()),
                        help="Chart type (default: bar)")
    parser.add_argument("--title", default="",
                        help="Slide title (default: palette name)")
    parser.add_argument("--subtitle", default="",
                        help="Slide subtitle (optional)")
    parser.add_argument("--data", default="",
                        help="Comma-separated numeric data values")
    parser.add_argument("--labels", default="",
                        help="Comma-separated data point labels")
    parser.add_argument("--list", action="store_true",
                        help="List all available palette names and exit")
    args = parser.parse_args()

    if args.list:
        print(f"Available palettes ({len(PALETTES)}):")
        for name in sorted(PALETTES.keys()):
            print(f"  {name}")
        sys.exit(0)

    data = _parse_data(args.data) if args.data else DEMO_DATA
    labels = _parse_labels(args.labels, len(data))

    html = generate_html(
        query=args.query,
        chart_type_key=args.chart_type,
        title=args.title,
        subtitle=args.subtitle,
        data=data,
        labels=labels,
    )

    out_path = Path(args.output)
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Cannot write '{args.output}': {exc}", file=sys.stderr)
        sys.exit(1)

    palette_name, _ = _lookup_palette(args.query)
    print(f"OK  {args.output}  (palette: {palette_name!r}  chart: {args.chart_type})")
    sys.exit(0)


if __name__ == "__main__":
    main()
