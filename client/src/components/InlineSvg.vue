<template>
  <div class="inline" v-html="svgContent"></div>
</template>

<script>
export default {
  props: {
    src: {
      type: String,
      required: true,
    },
    iconClass: {
      type: String,
    },
    iconStyle: {
      type: String,
    },
  },
  computed: {
    svgContent() {
      let { src, iconClass, iconStyle } = this

      let svgContent = require(`!html-loader!./../assets/${src}.svg`)

      let styledSvg = `<svg class="${iconClass ? iconClass : 'icon'}" style="${
        iconStyle ? iconStyle : ''
      }"`

      svgContent = svgContent.replace(/<svg/, styledSvg)
      return svgContent
    },
  },
}
</script>
