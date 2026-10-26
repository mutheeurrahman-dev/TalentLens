import os
import time
from playwright.sync_api import sync_playwright

os.makedirs('screenshots', exist_ok=True)

def capture_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 850})
        page = context.new_page()

        print("Navigating to TalentLens frontend...")
        page.goto("http://localhost:5173", wait_until="networkidle")
        time.sleep(2)

        # 1. Figure 8.1: Dashboard Overview
        page.click('button[data-testid="tab-overview"]')
        time.sleep(1)
        page.screenshot(path="screenshots/fig8_1_dashboard_overview.png")
        print("Captured fig8_1_dashboard_overview.png")

        # 2. Figure 8.2: Cloud Architecture Section
        # Scroll slightly to show Cloud Architecture nicely
        arch_elem = page.locator(".cloud-arch-card")
        if arch_elem.count() > 0:
            arch_elem.scroll_into_view_if_needed()
            time.sleep(1)
            page.screenshot(path="screenshots/fig8_2_cloud_architecture.png")
            print("Captured fig8_2_cloud_architecture.png")

        # 3. Figure 8.3: Candidate Pool (Unmatched / All Candidates)
        page.click('button[data-testid="tab-candidates"]')
        time.sleep(1)
        page.screenshot(path="screenshots/fig8_3_candidate_pool.png")
        print("Captured fig8_3_candidate_pool.png")

        # 4. Figure 8.4: Job Requirements Form
        page.click('button[data-testid="tab-requirements"]')
        time.sleep(1)
        # Fill in a realistic job requirement
        title_input = page.locator('input[placeholder*="Job Title"], input[placeholder*="role"], input[type="text"]').first
        if title_input.count() > 0:
            title_input.fill("Senior Full Stack Cloud Engineer")
        reqs_area = page.locator('textarea').first
        if reqs_area.count() > 0:
            reqs_area.fill(
                "Looking for a Senior Full Stack Cloud Engineer with 4+ years experience.\n"
                "Must-have skills: React, Node.js, Python, AWS Lambda, Docker, PostgreSQL, REST API, Git, TypeScript.\n"
                "Nice-to-have: Kubernetes, Redis, Terraform, GraphQL."
            )
        time.sleep(1)
        page.screenshot(path="screenshots/fig8_4_job_requirements.png")
        print("Captured fig8_4_job_requirements.png")

        # 5. Figure 8.5: Candidate Matching & Ranked Results
        match_btn = page.locator('button:has-text("Match"), button:has-text("Screen"), button:has-text("Evaluate")').first
        if match_btn.count() > 0:
            match_btn.click()
            time.sleep(2)
        # We should automatically be navigated to candidates tab with ranked scores!
        page.screenshot(path="screenshots/fig8_5_ranked_results.png")
        print("Captured fig8_5_ranked_results.png")

        # 6. Figure 8.6: Candidate Detail Modal
        # Click on the top candidate card or view details button
        inspect_btn = page.locator('button:has-text("View"), button:has-text("Details"), button:has-text("Inspect")').first
        if inspect_btn.count() > 0:
            inspect_btn.click()
            time.sleep(1)
            page.screenshot(path="screenshots/fig8_6_candidate_modal.png")
            print("Captured fig8_6_candidate_modal.png")
            # Close modal
            close_btn = page.locator('.modal-close-btn, button:has-text("Close"), button:has-text("✕")').first
            if close_btn.count() > 0:
                close_btn.click()
                time.sleep(0.5)

        # 7. Figure 8.7: Resume Upload Interface
        page.click('button[data-testid="tab-upload"]')
        time.sleep(1)
        page.screenshot(path="screenshots/fig8_7_resume_upload.png")
        print("Captured fig8_7_resume_upload.png")

        # 8. Figure 8.8: Candidate Table View (or Toggle to Table if available)
        page.click('button[data-testid="tab-candidates"]')
        time.sleep(1)
        # Check if table toggle exists
        table_toggle = page.locator('button:has-text("Table"), button[aria-label*="Table"], .view-mode-btn:has-text("Table")').first
        if table_toggle.count() > 0:
            table_toggle.click()
            time.sleep(1)
        page.screenshot(path="screenshots/fig8_8_candidate_table.png")
        print("Captured fig8_8_candidate_table.png")

        browser.close()
        print("All screenshots successfully captured!")

if __name__ == '__main__':
    capture_all()
