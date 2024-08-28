import argparse
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "/"

def ai_link_verification(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"AI-Driven Error: Unable to verify link {url}. Exception: {e}")
        return False

def dynamic_error_handling(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"AI-Driven Error Handling: Exception caught in {func.__name__}: {e}")
            # AI can suggest fixes or provide alternative methods here
            return None
    return wrapper

@dynamic_error_handling
def updateVersionHTML(base_path, base_url=BASE_URL):
    with open(base_path + "/Ax-main/website/_versions.json", "rb") as infile:
        versions = json.loads(infile.read())

    with open(base_path + "/new-site/versions.html", "rb") as infile:
        html = infile.read()

    versions.append("latest")

    def prepend_url(a_tag, base_url, version):
        href = a_tag.attrs["href"]
        if href.startswith("https://") or href.startswith("http://"):
            return href
        else:
            return "{base_url}versions/{version}{original_url}".format(
                base_url=base_url, version=version, original_url=href
            )

    for v in versions:
        soup = BeautifulSoup(html, "html.parser")

        # title
        title_link = soup.find("header").find("a")
        updated_link = prepend_url(title_link, base_url, v)
        if ai_link_verification(updated_link):
            title_link.attrs["href"] = updated_link
        else:
            print(f"AI-Driven Warning: Invalid link {updated_link} for version {v}")

        # nav
        nav_links = soup.find("nav").findAll("a")
        for link in nav_links:
            updated_link = prepend_url(link, base_url, v)
            if ai_link_verification(updated_link):
                link.attrs["href"] = updated_link
            else:
                print(f"AI-Driven Warning: Invalid link {updated_link} for version {v}")

        # version link
        t = soup.find("h2", {"class": "headerTitleWithLogo"}).find_next("a")
        updated_link = prepend_url(t, base_url, v)
        if ai_link_verification(updated_link):
            t.attrs["href"] = updated_link
        else:
            print(f"AI-Driven Warning: Invalid link {updated_link} for version {v}")
        h3 = t.find("h3")
        h3.string = v

        # output files
        with open(
            base_path + "/new-site/versions/{}/versions.html".format(v), "w"
        ) as outfile:
            outfile.write(str(soup))
        with open(
            base_path + "/new-site/versions/{}/en/versions.html".format(v), "w"
        ) as outfile:
            outfile.write(str(soup))

        print(f"AI-Driven Log: Successfully updated version {v}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Fix links in version.html files for Docusaurus site."
            "This is used to ensure that the versions.js for older "
            "versions in versions subdirectory are up-to-date and "
            "will have a way to navigate back to newer versions."
        )
    )
    parser.add_argument(
        "-p",
        "--base_path",
        metavar="path",
        required=True,
        help="Input directory for rolling out new version of site.",
    )
    args = parser.parse_args()
    updateVersionHTML(args.base_path)
