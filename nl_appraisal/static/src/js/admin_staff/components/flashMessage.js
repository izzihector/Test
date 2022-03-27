FlashMessage = {
    emits: ['closeMessage'],
    props: {
        message: {},
        type: {
            default: 'success'
        },
        duration: {
            default: 8000
        }
    },
    mounted() {
        setTimeout(() => {
            this.$emit('closeMessage')
        }, this.duration);
    },
    template: `
        <teleport to="main">
            <div :class="{'error-appraisal': type == 'error', 'success-appraisal': type == 'success'}" id="flash-message" class="mt-4 mr-4">
                <strong>{{ type }}</strong>
                <button class="close" style="font-size:17px" @click='$emit("closeMessage")'>x</button>
                <hr style='margin-top: 0px;margin-bottom::4px'/>
                {{message}}
            </div>
        </teleport>
    `
}