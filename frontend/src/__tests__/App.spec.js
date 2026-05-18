import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import App from '../App.vue'

describe('App', () => {
  it('renders the weather chat shell', () => {
    const wrapper = mount(App)

    expect(wrapper.text()).toContain('天气查询智能体')
    expect(wrapper.text()).toContain('输入城市名或天气问题')
    expect(wrapper.text()).toContain('北京今天天气怎么样？')
  })
})
