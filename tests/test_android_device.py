from ux_agent.android_device import extract_texts_from_uixml


def test_extract_texts_from_uixml_collects_text_and_content_desc() -> None:
    xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation='0'>
  <node text='首页' content-desc='' />
  <node text='' content-desc='保养icon' />
  <node text='小保养99元活动' content-desc='促销图' />
</hierarchy>
"""
    texts = extract_texts_from_uixml(xml)
    assert texts == ["首页", "保养icon", "小保养99元活动", "促销图"]
