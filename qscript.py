import os
import time
from playwright.sync_api import sync_playwright

PATH_TO_VIDEO_FOLDER = "./video"

def CaptureVideo_Magento(
    url: str,
    company_name: str,
    language: str,
    country: str,
    postcode: str,
    city: str,
    street: str,
    house_no: str
) -> str | None:

    if not url or "html.duckduckgo.com" in url:
        url = "https://duckduckgo.com/"

    cursor_init_script = (
        "const highlight = document.createElement('div');"
        "highlight.id = 'custom-cursor-highlight';"
        "highlight.style.position = 'fixed';"
        "highlight.style.width = '32px';"
        "highlight.style.height = '32px';"
        "highlight.style.backgroundColor = 'rgba(255, 235, 59, 0.4)';"
        "highlight.style.borderRadius = '50%';"
        "highlight.style.pointerEvents = 'none';"
        "highlight.style.zIndex = '2147483646';"
        "highlight.style.transform = 'translate(-50%, -50%)';"
        ""
        "const cursor = document.createElement('div');"
        "cursor.id = 'custom-svg-cursor';"
        "cursor.style.position = 'fixed';"
        "cursor.style.width = '24px';"
        "cursor.style.height = '24px';"
        "cursor.style.pointerEvents = 'none';"
        "cursor.style.zIndex = '2147483647';"
        "cursor.style.transform = 'translate(0, 0)';"
        "cursor.innerHTML = '<svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"white\" stroke=\"black\" stroke-width=\"1.5\"><polygon points=\"2,2 2,20 7,15 13,21 15,19 9,13 17,13\"/></svg>';"
        ""
        "const callout = document.createElement('div');"
        "callout.id = 'custom-callout';"
        "callout.style.position = 'fixed';"
        "callout.style.top = '20px';"
        "callout.style.left = '50%';"
        "callout.style.transform = 'translateX(-50%)';"
        "callout.style.backgroundColor = '#ffeb3b';"
        "callout.style.color = '#000';"
        "callout.style.fontSize = '16pt';"
        "callout.style.padding = '6px 14px';"
        "callout.style.borderRadius = '4px';"
        "callout.style.pointerEvents = 'none';"
        "callout.style.zIndex = '2147483645';"
        "callout.style.fontFamily = 'Arial, sans-serif';"
        "callout.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2);';"
        "callout.style.display = 'none';"
        ""
        "function appendCursor() {"
        "    if (document.body && !document.getElementById('custom-svg-cursor')) {"
        "        document.body.appendChild(highlight);"
        "        document.body.appendChild(cursor);"
        "        document.body.appendChild(callout);"
        "    }"
        "}"
        ""
        "if (document.readyState === 'loading') {"
        "    document.addEventListener('DOMContentLoaded', appendCursor);"
        "} else {"
        "    appendCursor();"
        "}"
        ""
        "document.addEventListener('mousemove', (e) => {"
        "    cursor.style.left = e.clientX + 'px';"
        "    cursor.style.top = e.clientY + 'px';"
        "    highlight.style.left = (e.clientX + 12) + 'px';"
        "    highlight.style.top = (e.clientY + 12) + 'px';"
        "});"
        ""
        "document.addEventListener('click', (e) => {"
        "    const ripple = document.createElement('div');"
        "    ripple.style.position = 'fixed';"
        "    ripple.style.left = e.clientX + 'px';"
        "    ripple.style.top = e.clientY + 'px';"
        "    ripple.style.width = '0px';"
        "    ripple.style.height = '0px';"
        "    ripple.style.backgroundColor = 'rgba(255, 235, 59, 0.6)';"
        "    ripple.style.borderRadius = '50%';"
        "    ripple.style.pointerEvents = 'none';"
        "    ripple.style.zIndex = '2147483645';"
        "    ripple.style.transform = 'translate(-50%, -50%)';"
        "    ripple.style.transition = 'width 0.4s ease-out, height 0.4s ease-out, opacity 0.4s ease-out';"
        "    document.body.appendChild(ripple);"
        "    setTimeout(() => {"
        "        ripple.style.width = '45px';"
        "        ripple.style.height = '45px';"
        "        ripple.style.opacity = '0';"
        "    }, 10);"
        "    setTimeout(() => ripple.remove(), 450);"
        "});"
        ""
        "window.ShowCallout = function(text) {"
        "    callout.innerText = text;"
        "    callout.style.display = 'block';"
        "};"
    )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            
            context = browser.new_context(
                record_video_dir=PATH_TO_VIDEO_FOLDER,
                record_video_size={"width": 1280, "height": 720},
                viewport={"width": 1280, "height": 720}
            )
            
            context.add_init_script(cursor_init_script)
            
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("load")
            time.sleep(1)

            page.evaluate("window.ShowCallout('Test text')")
            time.sleep(1)

            search_box = page.locator('textarea[name="q"]').first
            search_box.wait_for(state="visible", timeout=15000)
            
            box = search_box.bounding_box()
            if box:
                page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=25)
            
            search_box.click()
            time.sleep(0.5)

            query = f"Magento developer in {city}"
            for char in query:
                page.keyboard.type(char, delay=100)
            
            time.sleep(0.5)

            page.keyboard.press("Enter")

            result_item = page.locator('a[data-testid="result-title-a"]').first
            result_item.wait_for(state="visible", timeout=20000)
            time.sleep(1)

            res_box = result_item.bounding_box()
            if res_box:
                page.mouse.move(res_box["x"] + 15, res_box["y"] + 10, steps=25)
                time.sleep(0.5)
                result_item.click()
            else:
                result_item.click()
            
            time.sleep(2)

            video = page.video
            video_path = video.path()
            
            context.close()
            browser.close()

            os.makedirs(PATH_TO_VIDEO_FOLDER, exist_ok=True)
            safe_company_name = "".join(c if c.isalnum() else "_" for c in company_name)
            final_video_path = os.path.abspath(os.path.join(PATH_TO_VIDEO_FOLDER, f"{safe_company_name}.webm"))

            if os.path.exists(video_path):
                if os.path.exists(final_video_path):
                    os.remove(final_video_path)
                os.rename(video_path, final_video_path)
                return final_video_path

            return None
            
    except Exception as e:
        print(f"Error during video capture: {e}")
        return None